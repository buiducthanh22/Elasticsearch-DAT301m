import os

from django.db import models
from rest_framework.response import Response
from django.http import HttpResponse

from tool import database

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


credential_path = "project_smartsearch/data/myocr.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
os.environ['PG_USER'] = "postgres"
os.environ['PG_HOST'] = "172.20.0.1"
os.environ['PG_PORT'] = "5432"
os.environ['PG_PASSWORD'] = "postgres"
os.environ['ELASTICSEARCH_HOST'] = "172.20.0.1"
os.environ["ELASTICSEARCH_PORT"] = "9200"
os.environ['REDIS_HOST'] = "172.20.0.1"
os.environ['REDIS_PORT'] = "6379"
os.environ['REDIS_DB'] = "0"
os.environ['REDIS_AUTH'] = "123456"
os.environ['TOKENIZERS_PARALLELISM'] = "false"


class Image(models.Model):
    """
    This class is used to process information sent from the front-end.
    Args:
        models.Model: Base class for Django models.
    """
    name = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)

    def process_image(self, name, base64_data):
        """
        This function receives the name, base64_data to process
        and save to the database and synchronize to elastic.

        Args:
            name: the name of the image sent
            base64_data: the image is converted to base64

        Returns:
            Response: HttpResponse with status = 200.
        """
        try:
            database.Data_base().up_data(name, base64_data)
            database.Data_base().run_pgsync()
            return HttpResponse(status=200)
        except Exception as e:
            print(f"Error: {e}")
            return Response({'message': 'Error.'})


class Smart_search(models.Model):
    """
    An intelligent search processing model.

    Args:
        models.Model: Base class for Django models.
    """
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=10000)

    def __str__(self):
        """
        Returns a string representation of the object.

        Returns:
            name: name of the image
            image: image to display
        """
        return self.name, self.image
