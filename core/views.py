from functools import partial

from django.shortcuts import render
from .models import Boards, Columns, Cards
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters
from .serializers import (BoardSerializer,
                          ColumnSerializer,
                          CardSerializer,
                          UpdateCardSerializer)
from .filters import CardFilter
from rest_framework.response import Response
from rest_framework.decorators import action

# Create your views here.

class BoardViewSet(ModelViewSet):
    queryset = Boards.objects.all()
    serializer_class = BoardSerializer

    @action(detail=True, methods=['get'], url_path='board')
    def get_a_board(self, request, pk=None):
        board = self.get_object()
        columns = Columns.objects.filter(board=board)
        board_data = BoardSerializer(board).data
        columns_data = ColumnSerializer(columns, many=True).data
        return Response({
            "Board": board_data,
            "columns": columns_data
        })

class ColumnViewSet(ModelViewSet):
    queryset = Columns.objects.all()
    serializer_class = ColumnSerializer

    @action(detail=True, methods=['get'], url_path='cards')
    def get_cards(self, request, *args, **kwargs):
        column = self.get_object()
        cards = Cards.objects.filter(column=column)
        serializer = CardSerializer(cards, many=True)

        return Response(serializer.data)

class CardViewSet(ModelViewSet):
    queryset = Cards.objects.all()
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UpdateCardSerializer
        return CardSerializer

    def perform_create(self, serializer):
        # Save a new card when the create endpoint is hit
        serializer.save()

    @action(detail=True, methods=['patch'])
    def patch(self, request, *args, **kwargs):
        # Handle partial updates here
        instance = self.get_object()
        serializer = UpdateCardSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
