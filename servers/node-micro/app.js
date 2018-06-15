const micro = require('micro')
const graphqlHTTP = require("express-graphql");
const schema = require("./schema");

// The root provides a resolver function for each API endpoint
const server = micro(
    graphqlHTTP({
        schema: schema,
        graphiql: false
    }))

server.listen(4000)

