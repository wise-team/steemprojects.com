import graphene
import package.api.schema


class Query(package.api.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
