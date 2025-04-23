# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class BoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.group_name = f'board_{self.board_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'move_card':
            # Broadcast the card move to the group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'card_moved',
                    'payload': data['payload']
                }
            )

    async def card_moved(self, event):
        await self.send(text_data=json.dumps({
            'type': 'card_moved',
            'payload': event['payload']
        }))