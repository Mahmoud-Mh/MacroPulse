from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Indicator
from .serializers import IndicatorSerializer, IndicatorListSerializer


class IndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Indicators.
    """
    queryset = Indicator.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'category', 'name']
    search_fields = ['name', 'country', 'description']
    ordering_fields = ['last_update', 'value', 'name', 'country']
    ordering = ['-last_update']

    def get_serializer_class(self):
        if self.action == 'list':
            return IndicatorListSerializer
        return IndicatorSerializer

    @action(detail=False, methods=['get'])
    def categories(self):
        """
        Return list of unique categories.
        """
        categories = Indicator.objects.values_list('category', flat=True).distinct()
        return Response(sorted(categories))

    @action(detail=False, methods=['get'])
    def countries(self):
        """
        Return list of unique countries.
        """
        countries = Indicator.objects.values_list('country', flat=True).distinct()
        return Response(sorted(countries))

    @action(detail=False, methods=['get'])
    def latest(self):
        """
        Return the most recently updated indicators.
        """
        latest = self.get_queryset().order_by('-last_update')[:10]
        serializer = IndicatorListSerializer(latest, many=True)
        return Response(serializer.data)
