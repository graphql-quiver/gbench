from graphene import ID, Interface, ObjectType, Schema, List, Field, String

class Base(Interface):
    id = ID()
    def resolve_id(self, info):
        return "id"


class Query(ObjectType):
    class Meta:
        interfaces = (Base, )

    string = String()
    list_of_strings = List(String)
    list_of_objects = List(lambda: Query)
    list_of_interfaces = List(Base)

    def resolve_string(self, info):
        return string

    def resolve_list_of_strings(self, info):
        return list_of_strings

    def resolve_list_of_objects(self, info):
        return list_of_objects

    def resolve_list_of_interfaces(self, info):
        return list_of_objects


string = "Hello World!"
list_of_strings = (string, ) * 100
list_of_objects = (Query(), ) * 100


schema = Schema(query=Query)
