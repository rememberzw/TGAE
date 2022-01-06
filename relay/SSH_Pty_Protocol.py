import asyncio
import logging

log = logging.getLogger('relay')


class MyPtyProtocol(asyncio.Protocol):
    def __init__(self, terminal_audit):
        # noinspection PyBroadException
        try:
            asyncio.Protocol.__init__(self)
            self.chan = None
            self.trans = None
            self.terminal_audit = terminal_audit
        except Exception as exc:
            log.error('init error: {}'.format(exc))

    def connection_made(self, trans):
        # noinspection PyBroadException
        try:
            self.trans = trans
        except Exception as exc:
            log.error('connection made error: {}, {}'.format(trans, exc))

    def connection_lost(self, exc):
        try:
            if exc:
                log.error('connection lost error: {}'.format(exc))
            else:
                log.debug('connection closed.')

            if self.terminal_audit.login_success:
                self.terminal_audit.stream_end()

            self.chan.close()
            self.trans.close()
        except Exception as exc:
            log.error('connection lost error: {}'.format(exc))

    def data_received(self, data):
        try:
            log.debug('SERVER> ({:d}) {}'.format(len(data), data))
            self.terminal_audit.server_output(data)
            self.chan.write(data)
        except Exception as exc:
            log.error('write data error: {}'.format(exc))

    def eof_received(self):
        log.debug('receive eof.')
        self.chan.exit(0)
