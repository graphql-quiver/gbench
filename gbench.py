import os
import sys
import re
import argparse

import asyncio
from asyncio.subprocess import PIPE, STDOUT, DEVNULL
import json
import yaml
from datetime import timedelta
import fire


dir_path = os.path.dirname(os.path.realpath(__file__))

regex = re.compile(r'((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def parse_duration(time_str):
    if not time_str:
        return 0
    parts = regex.match(str(time_str))
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params).total_seconds()


async def run_wrk(endpoint, query, concurrency=20, duration=10):
    # wrk = await asyncio.create_subprocess_exec(
    #     'wrk2', '-R', str(500), '-t', '1', '-c', str(concurrency), '-d', str(int(duration)), '-s', 'misc/graphql.lua',
    #     endpoint, query, stdout=PIPE, stderr=PIPE)
    wrk = await asyncio.create_subprocess_exec(
        'wrk', '-t', '1', '-c', str(concurrency), '-d', str(int(duration)), '-s', 'misc/graphql.lua',
        endpoint, query, stdout=PIPE, stderr=PIPE)

    output, json_data = await wrk.communicate()
    print(output.decode('utf-8'))
    try:
        data = json.loads(json_data)
    except:
        raise Exception("Received invalid json from wrk: {}".format(json_data))

    response_json = data.pop('response', None)
    if response_json:
        try:
            response = json.loads(response_json)
        except:
            raise Exception("Received invalid json from the GraphQL query: {}".format(response_json))
    else:
        response = None
    retcode = await wrk.wait()

    return data, response



async def start_server(command, cwd, wait_for=None):
    server = await asyncio.create_subprocess_exec(*command.split(), cwd=cwd)

    # lines = []
    # async for line in server.stdout:
    #     print(line.decode("utf-8"),)

    # while True:
    #     line = await server.stdout.readline()
    #     print("READ",  line)
    #     if line:
    #         line = line.decode('utf-8')
    #         lines.append(line)
    #     else:
    #         break

    # while 1:
    #     line = await server.stderr.readline()
    #     print(line)
    #     if not line:
    #         break
    return server
    # asyncio.wait_for
    # retcode = await server.wait()


async def get_query_result(query_name, server_name, url, query_filename, warmup_duration=0, warmup_concurrency=1):
    print("- Running query {}".format(query_name, server_name))
    if warmup_duration:
        print("  > Warming up the server")
        await run_wrk(url, query_filename, concurrency=warmup_concurrency, duration=warmup_duration)
        await asyncio.sleep(2)
    print("  > Benchmarking")
    result, response = await run_wrk(url, query_filename)
    return ({
        "query_name": query_name,
        "server_name": server_name,
        "results": result,
    }, response)


async def endpoint_is_dead(endpoint):
    curl = await asyncio.create_subprocess_exec(
        'curl', endpoint, '-s', '-o', '/dev/null', '-w', '%{http_code}\n', stdout=PIPE, stderr=PIPE)
    output, _ = await curl.communicate()
    return int(output.decode('utf-8')) == 0


async def force_termination(pid):
    kill = await asyncio.create_subprocess_exec(
        'kill', '-9', str(pid))
    await kill.communicate()


async def bench_server(name, command, cwd, endpoint, queries, warmup_duration=0, command_ready_seconds=2, warmup_concurrency=1):
    print("Starting server: {}".format(name))
    if not await endpoint_is_dead(endpoint):
        print("- Can't start the server as there is a process already running on {}".format(endpoint))

    server = await start_server(command, cwd)
    await asyncio.sleep(command_ready_seconds)
    results = []
    try:
        for query in queries:
            result, response = None, None
            try:
                result, response = await get_query_result(query.get('name'), name, endpoint, query.get('filename'), warmup_duration, warmup_concurrency)
                results.append(
                    result
                )
                # We wait 2 seconds between trials
                await asyncio.sleep(2)
            except Exception as e:
                print("- Exception occured: {} - SKIPPING".format(str(e)))

            expected_result = query.get('expectedResult')
            if expected_result and expected_result != response:
                raise Exception("GraphQL response mismatch expected.\nReceived: {}\nExpected:{}".format(
                    result['response'], expected_result
                ))

        return results
    except:
        raise
    finally:
        print("Terminating server: {}".format(name))
        if server.returncode is None:
            server.terminate()
        await server.wait()
        await asyncio.sleep(1)
        # await force_termination(server.pid)
        await asyncio.sleep(1)
        print("Terminated")


class Program(object):
    """The GraphQL Benchmarking utility"""
    def dashboard(self, input):
        """Runs the dashboard for the provided input"""
        with open(input, 'r') as f:
            contents = f.read()
        bench_results = json.loads(contents)
        from dashboard import run_dash_server
        run_dash_server(bench_results, debug=True)

    def benchmark(self, config, output=None):
        """Starts a benchmark given config and an optional output file"""
        loop = asyncio.get_event_loop()
        server = loop.run_until_complete(_main(config, output))


async def _main(config, output):
    with open(config, 'r') as content_file:
        content = content_file.read()
        config = yaml.load(content)

        all_queries = config.get('queries')
        all_servers = config.get('servers')
        for query in all_queries:
            filename = query.get('expectedResultFilename')
            if filename:
                with open(filename, 'r') as content_file:
                    content = content_file.read()
                    query['expectedResult'] = json.loads(content)

    results = []
    for server in all_servers:
        server_name = server.get('name')
        server_run = server.get('run')
        server_command = server_run.get('command')
        server_cwd = server_run.get('cwd') or "./"
        server_wait = parse_duration(server_run.get('startupTime', 2))
        server_endpoint = server.get('endpoint')
        server_warmup = server.get('warmup') or {}
        server_warmup_duration = parse_duration(server_warmup.get('duration') or 0)
        server_warmup_concurrency = server_warmup.get('concurrency') or 1

        results += await bench_server(
            name=server_name,
            command=server_command,
            cwd=os.path.join(dir_path, server_cwd),
            endpoint=server_endpoint,
            queries=all_queries,
            warmup_duration=server_warmup_duration,
            warmup_concurrency=server_warmup_concurrency,
            command_ready_seconds=server_wait,
        )

    if output:
        with open(output, 'w') as output_file:
            output_file.write(json.dumps(results))

    from dashboard import run_dash_server
    run_dash_server(results)

if __name__ == "__main__":
    fire.Fire(Program)
