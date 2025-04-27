from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Indicator
from .serializers import IndicatorSerializer, IndicatorListSerializer, BulkIndicatorSerializer


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
        if self.action == 'bulk_create':
            return BulkIndicatorSerializer
        return IndicatorSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple indicators in a single request.
        """
        serializer = BulkIndicatorSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Update multiple indicators in a single request.
        """
        data = request.data
        if not isinstance(data, list):
            return Response(
                {'error': 'Expected a list of items'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated = []
        errors = []
        
        for item in data:
            try:
                indicator = Indicator.objects.get(id=item.get('id'))
                serializer = IndicatorSerializer(indicator, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            except Indicator.DoesNotExist:
                errors.append({'id': item.get('id'), 'error': 'Not found'})
        
        response_data = {
            'updated': updated,
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        return Response(response_data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Delete multiple indicators in a single request.
        """
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response(
                {'error': 'Expected a list of IDs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted = []
        errors = []
        
        for id in ids:
            try:
                indicator = Indicator.objects.get(id=id)
                indicator.delete()
                deleted.append(id)
            except Indicator.DoesNotExist:
                errors.append({'id': id, 'error': 'Not found'})
        
        response_data = {
            'deleted': deleted,
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        return Response(response_data)

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
