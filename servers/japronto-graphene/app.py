from japronto import Application
from ujson import dumps, loads
from graphql import graphql, GraphQLCachedBackend, GraphQLCoreBackend
from schema import schema
from graphql.backend.quiver_cloud import GraphQLQuiverCloudBackend

headers = {
    'Content-Type': 'application/json; charset=utf8'
}

DEFAULT_QUERY = '''
query BasicQuery {
  #listOfObjects {
  #  string
  #}
  listOfInterfaces {
    id
    ...on Query {
      string
    }
  }
}
'''


def json_response(request, data):
    return request.Response(
        text=dumps(data),
        headers=headers
    )


def get_json_body(request):
    return loads(request.body)


def basic_view(request):
    return json_response(request, {'hello':'Hello world!'})


def get_query_data(request):
    if request.body:
        if request.mime_type == "application/graphql":
            return {
                'query': request.body.decode("utf-8"),
                'operationName': request.query.get('operationName')
            }
        return get_json_body(request)
    else:
        # We are in test mode
        return {'query': DEFAULT_QUERY}

backend = GraphQLCachedBackend(GraphQLCoreBackend())
quiver_backend = GraphQLCachedBackend(GraphQLQuiverCloudBackend(
    "http://6ea643a71f96482bae042729c0eedad4:ed675996b9914c549189e2adbc8c0412@api.graphql-quiver.com"
))


def graphql_view(request):
    data = get_query_data(request)
    query = data.get('query')
    operation_name = data.get('operationName')

    result = graphql(schema, query, backend=backend, operation_name=operation_name, validate=False)
    return json_response(request, result.to_dict())


def quiver_view(request):
    # print(request.mime_type, request.body)
    data = get_query_data(request)
    query = data.get('query')
    operation_name = data.get('operationName')
    result = graphql(schema, query, backend=quiver_backend, operation_name=operation_name)
    return json_response(request, result.to_dict())


if __name__ == '__main__':
    app = Application()
    app.router.add_route('/basic', basic_view)
    app.router.add_route('/graphql', graphql_view)
    app.router.add_route('/quiver', quiver_view)
    app.run()
