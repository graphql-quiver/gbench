var express = require("express");
var graphqlHTTP = require("express-graphql");
var schema = require("./schema");

// The root provides a resolver function for each API endpoint

var app = express();
app.use(
  "/graphql",
  graphqlHTTP({
    schema: schema,
    graphiql: false
  })
);
app.listen(4000);
