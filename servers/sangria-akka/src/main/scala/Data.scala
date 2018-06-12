trait Base {
  def id: String
}

case class Query(
  id: String,
  string: String,
  listOfStrings: List[String]
  // listOfObjects: List[Query]
 ) extends Base

class Context {
  // val s = "Hello World!"
  // val base = Query(
  //   id="id",
  //   string=s,
  //   listOfStrings=List(s, s, s)
  // )

}
object Base {
  val string = "Hello World!"
  val obj = new Query(id="id", string=string, listOfStrings=List.fill(100)(string))
  val listOfObjects = List.fill(100)(obj)
}
