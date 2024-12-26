import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get board_id from the URL route and create the group name
        self.board_id = self.scope["url_route"]["kwargs"]["board_id"]
        self.board_group_name = f"board_{self.board_id}"

        # Add the WebSocket connection to the group for this board
        await self.channel_layer.group_add(
            self.board_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group when disconnected
        await self.channel_layer.group_discard(
            self.board_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse incoming WebSocket message
        data = json.loads(text_data)

        # Send the received message to the group
        await self.channel_layer.group_send(
            self.board_group_name,
            {
                "type": "board_update",  # Update the type to match the handler
                "message": data
            }
        )

    async def board_update(self, event):
        # Extract the message from the event and send it back to the WebSocket client
        message = event["message"]
        await self.send(text_data=json.dumps(message))
