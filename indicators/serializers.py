from rest_framework import serializers
from .models import Indicator


class IndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Indicator model with all fields.
    """
    class Meta:
        model = Indicator
        fields = '__all__'
        read_only_fields = ('previous_value', 'last_update')


class IndicatorListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for list views with fewer fields.
    """
    class Meta:
        model = Indicator
        fields = ('id', 'name', 'country', 'value', 'unit', 'last_update')
        read_only_fields = ('last_update',)


class BulkIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ['name', 'country', 'category', 'value', 'unit', 'description', 'source', 'last_update']
        extra_kwargs = {
            'last_update': {'required': False}
        } 