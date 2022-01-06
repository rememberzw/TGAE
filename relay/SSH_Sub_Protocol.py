import asyncio
import logging

log = logging.getLogger('relay')

# lock = asyncio.Lock()


class MySubProtocol(asyncio.SubprocessProtocol):
    def __init__(self, terminal_audit):
        # noinspection PyBroadException
        try:
            asyncio.SubprocessProtocol.__init__(self)
            self.chan = None
            self.trans = None
            self.terminal_audit = terminal_audit
            self.pid = None
        except Exception as exc:
            log.error('init error: {}'.format(exc))

    def connection_made(self, trans):
        # noinspection PyBroadException
        try:
            self.trans = trans
            self.pid = self.trans.get_pid()
            # lock.acquire()
            self.terminal_audit.onlines_control.add_online(self.pid, self.terminal_audit.tunnel_info)
            # lock.release()
        except Exception as exc:
            log.error('connection_made error: {}, {}'.format(trans, exc))

    def connection_lost(self, exc):
        # noinspection PyBroadException
        try:
            if exc:
                log.error('connection lost error: {}'.format(exc))
            else:
                log.debug('connection closed.')
            self.terminal_audit.onlines_control.pop_online(self.pid)
            self.chan.close()
            self.trans.close()
        except Exception as exc:
            log.error('connection lost error: {}'.format(exc))

    def eof_received(self):
        log.debug('receive eof.')
        self.chan.exit(0)
