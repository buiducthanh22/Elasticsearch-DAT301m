from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse

from .serializers import ImageSerializer
from .models import Image as Img
from tool import search_elastic

import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Img.objects.all()
    serializer_class = ImageSerializer
    """
    This class is used to process information received from
    the user interface
    """

    def create(self, request, *args, **kwargs):
        """This function is used to receive requests from the front-end,
        process them and return the front-end the HTTP response with
        status = 200.
        

        Args:
            request: The received request is a Json file.

        Returns:
            HttpResponse: The HTTP response with status = 200.
        """
        body1 = request.body.decode()
        data = json.loads(body1)
        images = json.loads(data['images'])
        for image in images:
            name = image['name']
            base64_data = image['image']
            Img().process_image(name, base64_data)
        return HttpResponse(status=200)


class SearchView(APIView, ):
    """
    This class is used to search on elasticsearch and
    return the front-end response
    """

    def get(self, request):
        """
        Get function to receive information from the front-end
        is key-query and slider_value and process it.

        Args:
            key_query: keywords entered by the user for processing.
            slider_value: minimum precision for display.

        Returns:
            response: HTTP response object
        """
        key_query = request.GET.get('query', '')
        slider_value = request.GET.get('sliderValue')
        response = Response\
        (search_elastic.Searched().main(key_query, slider_value))
        return response

def health_check(request):
    return JsonResponse({'status': 'ok'})