// Package starwars provides a example schema and resolver based on Star Wars characters.
//
// Source: https://github.com/graphql/graphql.github.io/blob/source/site/_core/swapiSchema.js
package main

// import (
// 	graphql "github.com/graph-gophers/graphql-go"
// )

var Schema = `
	schema {
		query: Query
	}

	interface Base {
		id: String
	}

	type Query implements Base {
		id: String
		string: String
		listOfStrings: [String]
		listOfObjects: [Query]
		listOfInterfaces: [Base]
	}
`

type base interface {
	ID()	*string
}

type query struct {
	base
	ID        string
	String      string
	// ListOfStrings   []string
	// ListOfObjects []query
}

type Resolver struct{
	q *query
}

type BaseResolver struct {
	base
}

var listOfObjects []*Resolver;
var listOfStrings []*string;
var listOfInterfaces []*BaseResolver;

var baseResolver Resolver;

func init() {
	var helloWorld string
	helloWorld = "Hello World!"
	// var ob query
	// ob = query {
	// 	ID: "id",
	// 	String: "Hello World!",
	// }
	baseResolver = Resolver{
		q: &query {
			ID: "id",
			String: "Hello World!",
		},
	}
	listOfStrings = make([]*string, 100)
	listOfObjects = make([]*Resolver, 100)
	listOfInterfaces = make([]*BaseResolver, 100)

	for i := 0; i < 100; i++ {
		listOfStrings[i] = &helloWorld
		listOfObjects[i] = &baseResolver
	}
}

func (r *Resolver) ID() *string {
	return &r.q.ID
}

func (r *Resolver) String() *string {
	return &r.q.String
}

func (r *Resolver) ListOfStrings() *[]*string {
	return &listOfStrings
}

func (r *Resolver) ListOfObjects() *[]*Resolver {
	return &listOfObjects
}

func (r *Resolver) ListOfInterfaces() *[]*BaseResolver {
	return &listOfInterfaces;
}

func (r *BaseResolver) ToQuery() (*Resolver, bool) {
	return &baseResolver, true
}
