from django.db.models import Count

from rest_framework.generics import ListAPIView, RetrieveAPIView

from package.models import Category, Project
from package.serializers import PackageSerializer


class PackageListAPIView(ListAPIView):
    model = Project
    paginate_by = 20


class PackageDetailAPIView(RetrieveAPIView):
    model = Project


class CategoryListAPIView(ListAPIView):
    model = Category
    paginate_by = 200


class Python3ListAPIView(ListAPIView):
    model = Project
    serializer_class = PackageSerializer
    paginate_by = 200

    def get_queryset(self):
        packages = Project.objects.filter(version__supports_python3=True)
        packages = packages.distinct()
        packages = packages.annotate(usage_count=Count("usage"))
        packages.order_by("-repo_watchers", "name")
        return packages


