import graphene
from graphene_django.types import DjangoObjectType
from package.models import Category


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class Query(object):
    all_categories = graphene.List(CategoryType)

    # @graphene.resolve_only_args
    # def resolve_all_categories(self, info, **kwargs):
    #     return Category.objects.all()
