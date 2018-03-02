import csv

from django.core.management.base import BaseCommand
from grid.models import Element, Grid, GridPackage, Feature
from package.models import Project


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']

        grid = Grid.objects.create(**{
            'title': 'test grid',
            'slug': 'testgrid',
            'description': 'test',
            'is_draft': False,
            'is_locked': False,
            'header': True,
        })

        with open('/app/grid/cvs_fixtures/{}'.format(filename)) as csvDataFile:
            csvReader = csv.reader(csvDataFile)

            project_slugs = next(csvReader)[1:]

            feature_rows = []
            for row in csvReader:
                feature_rows.append({
                    'name': row[0],
                    'values': row[1:]
                })

        for i, project_slug in enumerate(project_slugs):
            project = Project.objects.get(slug=project_slug)
            grid_package = GridPackage.objects.create(grid=grid, package=project)
            for feature_row in feature_rows:
                feature, _ = Feature.objects.get_or_create(grid=grid, title=feature_row['name'], description='')
                Element.objects.create(grid_package=grid_package, feature=feature, text=feature_row['values'][i])
