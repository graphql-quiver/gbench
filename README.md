# gbench

GBench is a GraphQL benchmarking tool. It's highly inspired by Hasura's work on [graphql-bench](https://github.com/hasura/graphql-bench/) but with different design and goals in mind.

Gbench will use a [config file](#config-file) to read the servers and queries to be executed.

## Requirements

If you want to run gbench locally, you will need Python 3.6+ and `wrk` working locally.

```shell
pip install -r requirements.txt
# For mac
brew install wrk
```

## Available commands

Gbench have currently two commands available

### Benchmark

`python gbench.py benchmark` will benchmark Servers and queries from a given [`config.yaml`](#config-file) and output into an optional json file (`results.json`)

```shell
python gbench.py benchmark config.yaml results.json
```

Also, after benchmarking a dashboard server will automatically run with the results.

### Dashboard

`python gbench.py dashboard results.json` will start a dashboard server using the given results file.

## Config file

The Gbench config file is in a `yaml` format. It have two main sections: `servers` and `queries`.

For servers:

```yaml
servers:
- name: Graphene
  # The endpoint to run the benchmark on
  endpoint: http://localhost:8080/graphql
  run:
    # The command to run
    command: python app.py
    # The path where the command is going to be executed
    cwd: servers/japronto-graphene/
    # The time we will wait before benchmarking
    startupTime: 2s

  # If we want to warmup the server before benchmarking
  warmup:
    concurrency: 1
    duration: 5s
```

For queries:

```yaml
queries:
- name: Basic
  # The filename where the query is going to be readed
  filename: queries/basic.graphql
  # This is optional, but if present will validate the response
  # of each of the GraphQL servers against the given file.
  expectedResultFilename: queries/basic.json
```

## Available languages

Currently, for benchmarking you will need to be able to execute the server locally.
That means that for benchmarking `go` you will need `go` installed locally.

This are the currently available languages for benchmark:

- Python (with Japronto)
- Node (Express)
- Sangia (Akka)
- Go

## Docker

You can build the dashboard image in docker by doing:

```
docker build -t quiver/gbench .
```

And to run the dashboard:

```
docker run -p 8050:8050 quiver/gbench
```
