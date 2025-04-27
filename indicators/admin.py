from django.contrib import admin
from django.db.models import Avg, Max, Min
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from .models import Indicator

class ValueRangeFilter(admin.SimpleListFilter):
    title = 'Value Range'
    parameter_name = 'value_range'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Low Values (< 0)'),
            ('medium', 'Medium Values (0-10)'),
            ('high', 'High Values (> 10)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(value__lt=0)
        if self.value() == 'medium':
            return queryset.filter(value__gte=0, value__lte=10)
        if self.value() == 'high':
            return queryset.filter(value__gt=10)

class UpdateFrequencyFilter(admin.SimpleListFilter):
    title = 'Update Frequency'
    parameter_name = 'update_frequency'

    def lookups(self, request, model_admin):
        return (
            ('daily', 'Updated Today'),
            ('weekly', 'Updated This Week'),
            ('monthly', 'Updated This Month'),
        )

    def queryset(self, request, queryset):
        now = datetime.now()
        if self.value() == 'daily':
            return queryset.filter(last_update__date=now.date())
        if self.value() == 'weekly':
            week_ago = now - timedelta(days=7)
            return queryset.filter(last_update__gte=week_ago)
        if self.value() == 'monthly':
            month_ago = now - timedelta(days=30)
            return queryset.filter(last_update__gte=month_ago)

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'country', 'value', 'unit', 'frequency', 
        'last_update', 'category', 'source', 'value_change'
    )
    list_filter = (
        'country', 'category', 'frequency', 'source',
        ValueRangeFilter, UpdateFrequencyFilter
    )
    search_fields = ('name', 'country', 'category', 'description')
    ordering = ('-last_update',)
    readonly_fields = ('previous_value', 'value_change')
    actions = ['export_to_csv', 'update_selected_indicators']
    date_hierarchy = 'last_update'
    list_per_page = 50
    list_select_related = True
    list_editable = ('value', 'unit')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'category', 'description')
        }),
        ('Values', {
            'fields': ('value', 'previous_value', 'value_change', 'unit')
        }),
        ('Metadata', {
            'fields': ('frequency', 'last_update', 'source')
        }),
    )

    def value_change(self, obj):
        if obj.previous_value is None:
            return "N/A"
        change = obj.value - obj.previous_value
        color = 'green' if change > 0 else 'red'
        return format_html(
            '<span style="color: {}">{:+.2f} {}</span>',
            color,
            change,
            obj.unit
        )
    value_change.short_description = 'Change'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            avg_value=Avg('value'),
            max_value=Max('value'),
            min_value=Min('value')
        )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data'):
            response.context_data['summary'] = self.get_summary()
        return response

    def get_summary(self):
        return {
            'total_indicators': Indicator.objects.count(),
            'countries': Indicator.objects.values('country').distinct().count(),
            'categories': Indicator.objects.values('category').distinct().count(),
            'avg_value': Indicator.objects.aggregate(avg=Avg('value'))['avg'],
        }

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="indicators.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Country', 'Value', 'Unit', 'Frequency',
            'Last Update', 'Category', 'Source', 'Previous Value'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.name, obj.country, obj.value, obj.unit,
                obj.frequency, obj.last_update, obj.category,
                obj.source, obj.previous_value
            ])
        
        return response
    export_to_csv.short_description = "Export selected indicators to CSV"

    def update_selected_indicators(self, request, queryset):
        from .tasks import update_indicator
        for indicator in queryset:
            update_indicator.delay(indicator.name)
        self.message_user(request, f"Started update for {queryset.count()} indicators")
    update_selected_indicators.short_description = "Update selected indicators"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('summary/', self.admin_site.admin_view(self.summary_view), name='indicators-summary'),
        ]
        return custom_urls + urls

    def summary_view(self, request):
        context = {
            'title': 'Indicators Summary',
            'summary': self.get_summary(),
            'opts': self.model._meta,
        }
        return render(request, 'admin/indicators/summary.html', context)
