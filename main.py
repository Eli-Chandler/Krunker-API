import websockets
import asyncio
import msgpack
from aiocapsolver.capsolver import AsyncCapSolver
import os
import logging

logging.basicConfig(level=logging.INFO)
class KrunkerWebSocket:
    def __init__(self, capsolver_api_key):
        self.is_ready = False
        self.solver = AsyncCapSolver(capsolver_api_key)
        self.response_events = {
            'profile': {}
        }

        '''Schema:
        profile = {
            'name': [
                {
                    'event': event, 
                    'data': {data}}
            ]
        }
        '''

    async def start(self):
        self.connect_task = asyncio.create_task(self.connect())

    async def connect(self):
        async with websockets.connect('wss://social.krunker.io/ws', origin='https://krunker.io') as ws:
            self.ws = ws
            await self.on_open()
            try:
                async for message in ws:
                    await self.on_message(message)
            finally:
                await self.on_close()

    async def on_message(self, message):
        message = msgpack.unpackb(message[:-2])
        logging.info('RECIEVED: %s', message)
        await self.handle_message(message)

    async def on_close(self):
        self.is_ready = False
        logging.info('Disconnected from websocket')

    async def on_open(self):
        self.is_ready = True
        logging.info('Connected to websocket')


    async def handle_message(self, message):
        handlers = {
            'cpt': self.handle_cpt,
            'pi': self.handle_pi,
            '0': self.handle_request_response
        }

        if message[0] in handlers:
            await handlers[message[0]](message)

    async def handle_cpt(self, message):
        self.is_ready = False
        logging.info('Solving captcha')
        solution = await self.solver.solve_hcaptcha('https://krunker.io/', '60a46f6a-e214-4aa8-b4df-4386e68dfde4')
        logging.info('Solved captcha: %s', solution)
        await self.send_system_message(['cptR', solution['gRecaptchaResponse']])
        self.is_ready = True

    async def handle_pi(self, message):
        await self.send_system_message(['po'])

    async def handle_request_response(self, message):
        handlers = {
            'profile': self.handle_profile_response
        }

        if message[1] in handlers:
            await handlers[message[1]](message)

    async def handle_profile_response(self, message):
        request = self.response_events['profile'][message[2]][0]
        request['event'].set()
        request['data'] = message[3]


    async def request_profile(self, username):
        message = [
            'r',
            'profile',
            username,
        ]

        event = asyncio.Event()

        if username not in self.response_events['profile']:
            self.response_events['profile'][username] = []
        self.response_events['profile'][username].append({'event': event, 'data': None})

        await self.send_client_message(message)

        await event.wait()
        return self.response_events['profile'][username].pop(0)['data']

    async def send_client_message(self, message):
        while not self.is_ready:
            await asyncio.sleep(0.1)

        logging.info('SENDING: %s', message)
        message = msgpack.packb(message) + b'\x00\x00'
        await self.ws.send(message)

    async def send_system_message(self, message):
        logging.info('SENDING: %s', message)
        message = msgpack.packb(message) + b'\x00\x00'
        await self.ws.send(message)



async def main():
    capsolver_api_key = os.environ.get('CAPSOLVER_API_KEY')
    kws = KrunkerWebSocket(capsolver_api_key)
    await kws.start()

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

