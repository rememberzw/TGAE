import sys
import asyncio
import logging

from manage import Manage_Handle
from etc import config

log = logging.getLogger('manage')


class ManageInterface:
    def __init__(self, myloop, onlines):
        # noinspection PyBroadException
        try:
            self.myloop = myloop
            self.manage_handle = Manage_Handle.ManageHandle(onlines)
        except Exception as exc:
            log.error('init error: {}'.format(exc))
            sys.exit(1)

    async def manage_server(self, reader, writer):
        # noinspection PyBroadException
        message = None
        try:
            data = await reader.read(1024)
            message = data.decode()
            addr = writer.get_extra_info('peername')
            log.info('received {} from {}'.format(message, addr))
        except Exception as exc:
            log.error('receive message error: {}'.format(exc))

        try:
            recv = self.manage_handle.handle_input(message)
            log.info('handle input recv: {}'.format(recv))

            writer.write(recv.encode())
            await writer.drain()
        except Exception as exc:
            log.error('write message error: {}'.format(exc))

        try:
            log.debug("close the client socket")
            writer.close()
        except Exception as exc:
            log.error('write close error: {}'.format(exc))

    async def start(self):
        log.info('localhost:{:d} is running...'.format(config.manage_port))
        # noinspection PyBroadException
        try:
            # coro = await asyncio.start_server(
            #     self.manage_server, config.sshd_ip, config.manage_port, loop = self.myloop
            # )
            await asyncio.start_server(self.manage_server, config.sshd_ip, config.manage_port, loop=self.myloop)
        except Exception as exc:
            log.error('start error: {}'.format(exc))
            sys.exit(1)
