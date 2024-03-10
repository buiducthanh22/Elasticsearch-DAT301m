from rest_framework import serializers

from .models import Image
from .models import Smart_search


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = ['name', 'label', 'vector', 'image']


class SearchSerializer(serializers.Serializer):

    class Meta:
        model = Smart_search
        fields = '__all__'
