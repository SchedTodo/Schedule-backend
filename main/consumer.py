from enum import Enum
import json
from channels.generic.websocket import AsyncWebsocketConsumer

connected_users = {}


class Apis(Enum):
    CONNECT = 'connect'
    LOGIN = 'login'


class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = None

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        if 'uid' in self.__dict__ and self.uid in connected_users:
            del connected_users[self.uid]
        self.uid = None

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)['message']
        api = text_data_json['api']
        data = text_data_json['data']
        print(text_data_json)

        if api == 'connect':
            uid = data['uid']
            self.uid = uid
            connected_users[uid] = self
            await send_message_to_user(uid, Apis.CONNECT, {})


async def send_message_to_user(uid, api: Apis, data):
    print(f'connected_users: {connected_users}')
    if uid in connected_users:
        await connected_users[uid].send(text_data=json.dumps({
            'message': {
                'api': api.value,
                'data': data
            }
        }))
        print('send_message_to_user', uid, api, data)
