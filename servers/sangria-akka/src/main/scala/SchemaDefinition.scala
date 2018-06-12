import sangria.execution.deferred.{Fetcher, HasId}
import sangria.schema._

import scala.concurrent.Future

/**
 * Defines a GraphQL schema for the current project
 */
object SchemaDefinition {
  /**
    * Resolves the lists of characters. These resolutions are batched and
    * cached for the duration of a query.
    */
  // val Base: InterfaceType[Context, Base] =
  //   InterfaceType(
  //     "Base",
  //     "",
  //     () ⇒ fields[Context, Base](
  //       Field("id", StringType,
  //         Some("The id of the character."),
  //         resolve = _.value.id),
  //     ))

  val Query: ObjectType[Context, Query] =
    ObjectType(
      "Query",
      "",
      // interfaces[Context, Query](Base),
      () => fields[Context, Query](
        Field("id", StringType,
          Some(""),
          resolve = _.value.id),
        Field("string", StringType,
          Some(""),
          resolve = _.value.string),
        Field("listOfStrings", ListType(StringType),
          Some(""),
          resolve = _.value.listOfStrings),
        Field("listOfObjects", ListType(Query),
          Some(""),
          resolve = c => Base.listOfObjects),
      ))

  val ExampleSchema = Schema(Query)
}
