from channels.testing import WebsocketCommunicator
from django.test import TestCase
from channels.layers import get_channel_layer
from taskifyAPI.routings import websocket_urlpatterns  # Ensure correct import
import json
from .models import Boards, Columns, Cards
from users.models import User
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path


# Define your consumer routing inside the test
class BoardConsumerTestCase(TestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(firstname='Test', lastname='User', email='a@a.com', password='password123')
        self.token = Token.objects.create(user=self.user)

        # Create test data for boards, columns, and cards
        self.board = Boards.objects.create(title='Test Board',
                                           user=self.user)  # Make sure the board has a user relation
        self.column = Columns.objects.create(title='To Do', board=self.board)
        self.card = Cards.objects.create(task='Test Task', column=self.column, position=1)

    async def test_websocket_connect_and_receive(self):
        # Ensure that the WebSocket routing is passed correctly as a callable
        application = ProtocolTypeRouter({
            "websocket": URLRouter(websocket_urlpatterns),
        })

        # Set the WebSocket URL with the board ID and the Authorization header
        communicator = WebsocketCommunicator(
            application,
            f"/ws/board/{self.board.id}/",
            headers=[
                (b"Authorization", f"Token {self.token.key}".encode("utf-8"))
            ]
        )

        # Establish WebSocket connection
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Prepare a test move card event
        move_data = {
            'type': 'board_update',
            'message': {
                'type': 'card_moved',
                'card_id': self.card.id,
                'new_position': 2,
                'target_column_id': self.column.id,
            }
        }

        # Send a message to the group (simulating the move)
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f'board_{self.board.id}',
            move_data
        )

        # Receive the message from the consumer
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'card_moved')
        self.assertEqual(response['card_id'], self.card.id)
        self.assertEqual(response['new_position'], 2)
        self.assertEqual(response['target_column_id'], self.column.id)

        # Close the WebSocket connection
        await communicator.disconnect()

    @sync_to_async
    def create_board(self):
        # Helper method to create a board with the database synced to the test thread
        return Boards.objects.create(title="Test Board")
