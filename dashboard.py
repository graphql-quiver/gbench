#!/usr/bin/env python3

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import click

import json
import itertools

import sys
import argparse

def compute_xs(program_rps_map):
    # l = list(set(itertools.chain(*[d.keys() for d in program_rps_map.values()])))
    return list(program_rps_map.keys())

def compute_ys(xs, rps_map, f):
    ys = []
    for x in xs:
        stat = rps_map.get(x)
        y = f(stat) if stat else None
        ys.append(y)
    return ys

def get_data(results, fn):
    all_servers = {result['server_name']:True for result in results}.keys()

    # print(program_rps_map)
    ys = []
    for server_name in all_servers:
        query_results = [result for result in results if result['server_name'] == server_name]
        server_name_results = {
            result['query_name']: result['results'] for result in query_results
        }
        dataRow = {
            "x" : list(server_name_results.keys()),
            "y": list(map(fn, server_name_results.values())),
            "type": "bar",
            "name": server_name
        }
        ys.append(dataRow)
    return ys

def get_ymetric_fn(yMetric, on='latency'):
    if yMetric == "P95":
        yMetricFn = lambda x: x[on]['dist']['95']
    elif yMetric == "P98":
        yMetricFn = lambda x: x[on]['dist']['98']
    elif yMetric == "P99":
        yMetricFn = lambda x: x[on]['dist']['99']
    elif yMetric == "MIN":
        yMetricFn = lambda x: x[on]['min']
    # elif yMetric == "ERRORS":
    #     yMetricFn = lambda x: sum(x['summary']['errors'].values())
    elif yMetric == "MAX":
        yMetricFn = lambda x: x[on]['max']
    else:
        yMetricFn = lambda x: x[on]['mean']

    if on == 'latency':
        return lambda x: None if round(yMetricFn(x)/1000, 2) > 1000 else round(yMetricFn(x)/1000, 2)
    
    return lambda x: int(yMetricFn(x))


def run_dash_server(bench_results, debug=False):

    all_queries = set([result['query_name'] for result in bench_results])
    app = dash.Dash()

    app.layout = html.Div(children=[

        # html.Label('Benchmark'),
        # dcc.Dropdown(
        #     id='benchmark-index',
        #     options=[{'label': query_name, 'value': query_name} for query_name in all_queries],
        #     value=next(iter(all_queries))
        # ),

        html.Label('Response time metric'),
        dcc.Dropdown(
            id='response-time-metric',
            options=[
                {'label': 'P95', 'value': 'P95'},
                {'label': 'P98', 'value': 'P98'},
                {'label': 'P99', 'value': 'P99'},
                {'label': 'Min', 'value': 'MIN'},
                {'label': 'Max', 'value': 'MAX'},
                {'label': 'Average', 'value': 'AVG'},
                {'label': 'Mean', 'value': 'MEAN'},
                # {'label': 'Errors', 'value': 'ERRORS'},
            ],
            value='P95'
        ),

        dcc.Graph(id='response-time-vs-query'),
        dcc.Graph(id='requests-vs-query'),
    ])

    @app.callback(
        Output('response-time-vs-query', 'figure'),
        [
            # Input('benchmark-index', 'value'),
            Input('response-time-metric', 'value')
        ]
    )
    def updateGraph(yMetric):
        # print(bench_results)
        figure={
            'data': get_data(bench_results, get_ymetric_fn(yMetric, on='latency')),
            'layout': {
                'yaxis' : {
                    'title': "Response time ({}) in ms".format(yMetric)
                },
                'xaxis' : {
                    'title': "Server"
                },
                'title' : 'Response time vs Query by server'
            }
        }
        return figure

    @app.callback(
        Output('requests-vs-query', 'figure'),
        [
            # Input('benchmark-index', 'value'),
            Input('response-time-metric', 'value')
        ]
    )
    def updateGraph(yMetric):
        # print(bench_results)
        figure={
            'data': get_data(bench_results, get_ymetric_fn(yMetric, on='requests')),
            'layout': {
                'yaxis' : {
                    'title': "Requests/s ({})".format(yMetric)
                },
                'xaxis' : {
                    'title': "Server"
                },
                'title' : 'Reqs/s vs Query by server'
            }
        }
        return figure

    app.run_server(host="0.0.0.0", debug=debug)
