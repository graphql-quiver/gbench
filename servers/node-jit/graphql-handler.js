const httpErrors = require('http-errors');
const {getGraphQLParams} = require("express-graphql")
const graphql = require('graphql');
const LRU = require("lru-cache")
const {compileQuery} = require("graphql-jit");


module.exports = function setupHandler(schema, disableLeafSerialization) {
    const cache = LRU({max: 100});
    return function graphqlMiddleware(request, response) {
        // Promises are used as a mechanism for capturing any thrown errors during
        // the asynchronous process below.

        // Parse the Request to get GraphQL request parameters.
        return getGraphQLParams(request).then(function (graphQLParams) {

            // Collect information from the options data object.
            let context = request;
            let rootValue = undefined;

            let validationRules = graphql.specifiedRules;

            // GraphQL HTTP only supports GET and POST methods.
            if (request.method !== 'GET' && request.method !== 'POST') {
                response.setHeader('Allow', 'GET, POST');
                throw httpErrors(405, 'GraphQL only supports GET and POST requests.');
            }

            // Get GraphQL params from the request and POST body data.
            const query = graphQLParams.query;
            const variables = graphQLParams.variables;
            const operationName = graphQLParams.operationName;

            // If there is no query, but GraphiQL will be displayed, do not produce
            // a result, otherwise return a 400: Bad Request.
            if (!query) {
                throw httpErrors(400, 'Must provide query string.');
            }
            let cached = cache.get(query + operationName);
            if (!cached) {
                // GraphQL source.
                let source = new graphql.Source(query, 'GraphQL request');
                let documentAST;
                // Parse source to AST, reporting any syntax error.
                try {
                    documentAST = graphql.parse(source);
                } catch (syntaxError) {
                    // Return 400: Bad Request if any syntax errors errors exist.
                    response.statusCode = 400;
                    return {errors: [syntaxError]};
                }

                // Validate AST, reporting any errors.
                let validationErrors = graphql.validate(schema, documentAST, validationRules);
                if (validationErrors.length > 0) {
                    // Return 400: Bad Request if any validation errors exist.
                    response.statusCode = 400;
                    return {errors: validationErrors};
                }

                // Only query operations are allowed on GET requests.
                if (request.method === 'GET') {
                    // Determine if this GET request will perform a non-query.
                    let operationAST = graphql.getOperationAST(documentAST, operationName);
                    if (operationAST && operationAST.operation !== 'query') {

                        // Otherwise, report a 405: Method Not Allowed error.
                        response.setHeader('Allow', 'POST');
                        throw httpErrors(405, 'Can only perform a ' + operationAST.operation + ' operation ' + 'from a POST request.');
                    }
                }

                cached = compileQuery(schema, documentAST, operationName, {disableLeafSerialization});
                cache.set(query + operationName, cached)
            }

            // Perform the execution, reporting any errors creating the context.
            try {
                return cached.query(rootValue, context, variables);
            } catch (contextError) {
                // Return 400: Bad Request if any execution context errors exist.
                response.statusCode = 400;
                return {errors: [contextError]};
            }
        }).catch(function (error) {
            // If an error was caught, report the httpError status, or 500.
            response.statusCode = error.status || 500;
            return {errors: [error]};
        }).then(function (result) {
            // If no data was included in the result, that indicates a runtime query
            // error, indicate as such with a generic status code.
            // Note: Information about the error itself will still be contained in
            // the resulting JSON payload.
            // http://facebook.github.io/graphql/#sec-Data
            if (response.statusCode === 200 && result && !result.data) {
                response.statusCode = 500;
            }
            // Format any encountered errors.
            if (result && result.errors) {
                result.errors = result.errors.map(graphql.formatError);
            }
            // At this point, result is guaranteed to exist, as the only scenario
            // where it will not is when showGraphiQL is true.
            if (!result) {
                throw httpErrors(500, 'Internal Error');
            }

            return result
        });
    };

}
