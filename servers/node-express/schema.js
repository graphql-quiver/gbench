var {
  GraphQLSchema,
  GraphQLObjectType,
  GraphQLString,
  GraphQLInterfaceType,
  GraphQLList
} = require("graphql");

var string = "Hello World!";
var listOfStrings = Array(100).fill(string);
var listOfObjects = Array(100).fill({});

var Base = new GraphQLInterfaceType({
  name: "Base",
  fields: {
    id: {
      type: GraphQLString
    }
  }
});
var Query = new GraphQLObjectType({
  name: "Query",
  interfaces: [Base],
  fields: () => ({
    id: {
      type: GraphQLString,
      resolve: () => "id"
    },
    string: {
      type: GraphQLString,
      resolve: () => string
    },
    listOfStrings: {
      type: GraphQLList(GraphQLString),
      resolve: () => listOfStrings
    },
    listOfObjects: {
      type: GraphQLList(Query),
      resolve: () => listOfObjects
    },
    listOfInterfaces: {
      type: Base,
      resolve: () => listOfObjects
    }
  })
});

schema = new GraphQLSchema({ query: Query });
module.exports = schema;
