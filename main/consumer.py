import json
from channels.generic.websocket import AsyncWebsocketConsumer


connected_users = {}


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        if self.uid in connected_users:
            del connected_users[self.uid]
        pass

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)['message']
        api = text_data_json['api']
        data = text_data_json['data']
        print(text_data_json)

        if api == 'login':
            uid = data['uid']
            self.uid = uid
            connected_users[uid] = self


async def send_message_to_user(uid, data):
    print(f'connected_users: {connected_users}')
    if uid in connected_users:
        await connected_users[uid].send(text_data=json.dumps({
            'message': data
        }))
        print('send_message_to_user', uid, data)
