from django.shortcuts import get_object_or_404
from .models import Boards, Columns, Cards
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction, models
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardSerializer, ColumnSerializer, CardSerializer, UpdateCardSerializer
from asgiref.sync import async_to_sync
from channels.layers import channel_layers, get_channel_layer


class BoardViewSet(ModelViewSet):
    queryset = Boards.objects.all()
    serializer_class = BoardSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='board')
    def retrieve_with_columns_and_cards(self, request, pk=None):
        board = self.get_object()
        columns = Columns.objects.filter(board=board).order_by("order")
        columns_with_cards = [
            {
                **ColumnSerializer(column).data,
                "cards": CardSerializer(Cards.objects.filter(column=column).order_by("position"), many=True).data,
            }
            for column in columns
        ]
        board_data = self.get_serializer(board).data
        board_data["columns"] = columns_with_cards
        return Response(board_data)

    def get_queryset(self):
        return Boards.objects.filter(user=self.request.user)


class ColumnViewSet(ModelViewSet):
    queryset = Columns.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='cards')
    def get_cards(self, request, *args, **kwargs):
        column = self.get_object()
        cards = Cards.objects.filter(column=column).order_by("position")
        return Response(CardSerializer(cards, many=True).data)


class CardViewSet(ModelViewSet):
    queryset = Cards.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateCardSerializer
        return CardSerializer

    @action(detail=True, methods=['patch'], url_path='move')
    def move_card(self, request, *args, **kwargs):
        instance = self.get_object()
        target_column_id = request.data.get('target_column_id')
        new_position = request.data.get('new_position')

        try:
            target_column = get_object_or_404(Columns, id=target_column_id)
            if not isinstance(new_position, int):
                return Response({"error": "Couldn't reposition the card"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Update positions in the current column
                Cards.objects.filter(
                    column=instance.column,
                    position__gt=instance.position,
                ).update(position=models.F('position') - 1)

                Cards.objects.filter(
                    column=target_column,
                    position__gte=new_position,
                ).update(position=models.F('position') + 1)

                # Move the card
                instance.column = target_column
                instance.position = new_position
                instance.save()

                channel_layers = get_channel_layer()
                board_name = f"Board_{instance.column.board.id}"
                async_to_sync(channel_layers.group_send) (
                    board_name,
                    {
                        "type": "Board update",
                        "message": {
                        "card_id": instance.id,
                        "New_position": new_position,
                        "target_column_id": target_column_id
                        }
                    }
                )


            return Response(UpdateCardSerializer(instance).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
