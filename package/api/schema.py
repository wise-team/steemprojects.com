import graphene
from graphene_django.types import DjangoObjectType
from package.models import Category, Project, ProjectImage


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ('title', 'description')


class ProjectType(DjangoObjectType):
    repository_url = graphene.Field(graphene.String)

    class Meta:
        model = Project
        fields = ('name', 'description', 'url', 'category', 'images',)

    def resolve_repository_url(self, info):
        return self.repo_url


class ProjectImageType(DjangoObjectType):
    class Meta:
        model = ProjectImage


class Query(object):
    categories = graphene.List(CategoryType)
    projects = graphene.List(ProjectType)

    def resolve_categories(self, info, **kwargs):
        return Category.objects.all()

    def resolve_projects(self, info, **kwargs):
        return Project.objects.all()
