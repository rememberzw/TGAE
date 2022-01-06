import os
import sys
import asyncio
import asyncssh
import pty
import termios
import struct
import logging
import functools
import fcntl
import signal

from relay.SSH_Sub_Protocol import MySubProtocol
from relay.SSH_Pty_Protocol import MyPtyProtocol
from etc import config

log = logging.getLogger('relay')


class MySSHServerSession(asyncssh.SSHServerSession):
    def __init__(self, loop, terminal_audit):
        # noinspection PyBroadException
        try:
            asyncssh.SSHServerSession.__init__(self)
            self.loop = loop
            self.terminal_audit = terminal_audit
            self.chan = None

            self.env = None
            self.term_env = None
            self.term_type = None
            self.term_tu = None
            self.term_size = None

            self.master = None
            self.slave = None

            self.pty_pipe = None
            self.pty_trans = None
            self.pty_proto = None

            self.sub_trans = None
            self.sub_proto = None
        except Exception as exc:
            log.error('init error: {}'.format(exc))

    def connection_made(self, chan):
        # noinspection PyBroadException
        try:
            self.chan = chan
        except Exception as exc:
            log.error('connection_made error: {}'.format(exc))

    def connection_lost(self, exc):
        # noinspection PyBroadException
        try:
            if exc:
                log.error('connection_lost error: {}'.format(exc))
            else:
                log.debug('connection closed.')
            # self.chan.close()
            self.pty_trans.close()
            self.sub_trans.close()
            self.pty_pipe.close()
        except Exception as exc:
            log.error('connection_lost error: {}'.format(exc))

    def session_started(self):
        # noinspection PyBroadException
        try:
            dest_info = 'Connecting to target host ({}:{:d})\r\n'.format(
                self.terminal_audit.ast.dip, self.terminal_audit.ast.dport)
            self.chan.write(dest_info.encode())
            asyncio.run_coroutine_threadsafe(self.forward_to(), self.loop)
        except Exception as exc:
            log.error('session_started error: {}'.format(exc))

    def pty_requested(self, term_type, term_size, term_modes):
        log.debug('pty_requested: ({}, {}, {})'.format(term_type, term_size, term_modes))
        return True

    def shell_requested(self):
        # noinspection PyBroadException
        try:
            log.debug('shell_requested')
            self.term_env = {}

            self.env = self.chan.get_environment()
            log.debug('env: {}'.format(self.env))
            self.term_env['LANG'] = self.env.get('LANG')
            self.term_env['LC_CTYPE'] = self.env.get('LC_CTYPE')

            self.term_type = self.chan.get_terminal_type()
            log.debug('term_type: {}'.format(self.term_type))
            self.term_env['TERM'] = self.term_type

            self.term_size = self.chan.get_terminal_size()
            log.debug('term_size: {}'.format(str(self.term_size)))
            self.terminal_audit.terminal_parse.resize(self.term_size[1], self.term_size[0])

            # self.term_mode = self.chan.get_terminal_mode()
            # log.debug('term_type: {}'.format(self.term_mode))
        except Exception as exc:
            log.error('shell_requested error: {}'.format(exc))
        return True

    def terminal_size_changed(self, width, height, pixwidth, pixheight):
        # noinspection PyBroadException
        try:
            log.debug('terminal_size_changed: ({}, {}, {}, {})'.format(width, height, pixwidth, pixheight))
            # TIOCSWINZ and TIOCGWINSZ ?????
            fcntl.ioctl(self.master, termios.TIOCSWINSZ, struct.pack('HHHH', height, width, pixheight, pixwidth))
            self.sub_trans.send_signal(signal.SIGWINCH)
            self.terminal_audit.terminal_parse.resize(height, width)
        except Exception as exc:
            log.error('terminal_size_changed error: {}'.format(exc))

    def data_received(self, data, datatype):
        # noinspection PyBroadException
        try:
            log.debug('CLIENT> ({:d}) {}'.format(len(data), data))
            res, res_info = self.terminal_audit.client_input(data)
            if res:
                os.write(self.master, data)
                if res_info == 'Exit':
                    self.chan.exit(0)
                    self.pty_trans.close()
                    self.sub_trans.close()
                    self.pty_pipe.close()
            else:
                os.write(self.master, self.terminal_audit.ctlint)
                self.chan.write(res_info.encode())
        except Exception as exc:
            log.error('data_received write data error: {}'.format(exc))

    def eof_received(self):
        log.debug('eof_received.')
        self.chan.exit(0)

    def signal_received(self, my_signal):
        log.debug('signal_received: {}'.format(my_signal))

    def break_received(self, my_signal):
        log.debug('break_received: {}'.format(my_signal))
        self.eof_received()

    async def forward_to(self):
        # noinspection PyBroadException
        try:
            self.master, self.slave = pty.openpty()
            log.debug('open pty: {}, {}'.format(self.master, self.slave))
            self.pty_pipe = open(self.master, 'rb+', 0)
            self.pty_trans, self.pty_proto = await self.loop.connect_read_pipe(
                functools.partial(MyPtyProtocol, self.terminal_audit), self.pty_pipe)
            log.debug('connect read pipe return: {} {} {}'.format(self.pty_trans, self.pty_proto, self.pty_pipe))
            self.pty_proto.chan = self.chan
        except Exception as exc:
            log.error('open pty error: {}'.format(exc))
            sys.exit(1)

        # noinspection PyBroadException
        try:
            # TIOCSWINZ and TIOCGWINSZ ?????
            fcntl.ioctl(
                self.master,
                termios.TIOCSWINSZ,
                struct.pack('HHHH', self.term_size[1], self.term_size[0], self.term_size[3], self.term_size[2])
            )
        except Exception as exc:
            log.error('ioctl windows size error: {}'.format(exc))
            sys.exit(1)

        # noinspection PyBroadException
        try:
            cmd = [config.python_path, '-m', 'relay.SSH_Client']
            log.debug('cmd: {} {} {}'.format(cmd, str(self.terminal_audit.tunnel_info), str(self.term_env)))

            self.sub_trans, self.sub_proto = await self.loop.subprocess_exec(
                    functools.partial(MySubProtocol, self.terminal_audit),
                    cmd[0], cmd[1], cmd[2], str(self.terminal_audit.tunnel_info), str(self.term_env),
                    stdin=self.slave, stdout=self.slave, stderr=self.slave,
                    start_new_session=True,
                    close_fds=True
                    )
            self.sub_proto.chan = self.chan
            # Important.the parent thread must close slave pty.
            os.close(self.slave)
        except Exception as exc:
            log.error('exec subprocess error: {}'.format(exc))
            sys.exit(1)
