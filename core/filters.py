from django_filters import rest_framework as filters
from .models import Cards
class CardFilter(filters.FilterSet):
    column = filters.NumberFilter(field_name='column', lookup_expr='exact')

    class Meta:
        model = Cards
        fields = ['column']
