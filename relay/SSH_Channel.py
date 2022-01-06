import os
import paramiko
import threading
import traceback
import pty
import logging
from termios import TIOCSWINSZ
import struct
from fcntl import ioctl
import subprocess
import signal

from etc import config
from lib import Channel_Request

log = logging.getLogger('paramiko')


class SSHChannel(paramiko.ServerInterface):
    def __init__(self, terminal_audit):
        self.event = threading.Event()
        self.terminal_audit = terminal_audit

        self.channel = None

        self.term_env = dict()
        self.term_size = dict()

        self.master = None
        self.slave = None
        self.master_pty_pipe = None

        self.proc = None

        self.keep_running = True

    def get_banner(self):
        banner = (config.banner, 'en-US')
        return banner

    def check_auth_none(self, username):
        log.debug('check_auth_none:{}'.format(username))
        return paramiko.AUTH_FAILED

    def check_auth_password(self, username, password):
        try:
            log.debug('validate_password username={}, password={}'.format(username, password))

            if config.channel_request == 'yes':
                channel_request = Channel_Request.ChannelRequest(username, password)
                result, tunnel_json = channel_request.get_channel()
                if not result:
                    return paramiko.AUTH_FAILED
                else:
                    username = tunnel_json
                    password = 'VG9tJkplcnJ5'

            if self.terminal_audit.process_tunnel_info(username, password):
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        except Exception as exc:
            log.error('connection made error: {}'.format(traceback.print_exc()))
            return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        log.debug('check_channel_request:{},{}'.format(kind, chanid))
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        log.debug('get_allowed_auths: {}'.format(username))
        return "password"

    def check_channel_shell_request(self, channel):
        log.debug('check_channel_shell_request: {}'.format(channel))
        self.channel = channel
        log.debug('chanid:{}'.format(self.channel.get_id()))
        self.event.set()
        self.forward_to()
        return True

    def check_channel_pty_request(self,
                                  channel,
                                  term, width, height, pixelwidth, pixelheight,
                                  modes):
        log.debug('check_channel_pty_request:{},{},{},{},{},{},{}'.format(
            channel, term, width, height, pixelwidth, pixelheight, modes))

        self.term_env['TERM'] = term.decode()

        self.term_size['width'] = width
        self.term_size['height'] = height
        self.term_size['pixelwidth'] = pixelwidth
        self.term_size['pixelheight'] = pixelheight

        self.terminal_audit.terminal_parse.resize(self.term_size['height'], self.term_size['width'])
        return True

    def check_channel_env_request(self,
                                  channel,
                                  name,
                                  value):
        log.debug('check_channel_env_request:{},{},{}'.format(
            channel, name, value))

        self.term_env[name.decode()] = value.decode()
        return True

    def check_channel_window_change_request(self,
                                            channel,
                                            width, height, pixelwidth, pixelheight):
        log.debug('check_channel_window_change_request:{},{},{},{}'.format(
            width, height, pixelwidth, pixelheight))

        ioctl(self.master, TIOCSWINSZ, struct.pack(
            'HHHH',
            height,
            width,
            pixelheight,
            pixelwidth
        ))
        if self.proc:
            self.proc.send_signal(signal.SIGWINCH)
        self.terminal_audit.terminal_parse.resize(self.term_size['height'], self.term_size['width'])
        return True

    def forward_to(self):
        # noinspection PyBroadException
        try:
            self.master, self.slave = pty.openpty()
            log.debug('open pty: {}, {}'.format(self.master, self.slave))

            self.master_pty_pipe = open(self.master, 'rb+', 0)
        except Exception as exc:
            log.error('open pty error: {}'.format(traceback.print_exc()))
            return

        # noinspection PyBroadException
        try:
            # TIOCSWINZ and TIOCGWINSZ ?????
            ioctl(
                self.master,
                TIOCSWINSZ,
                struct.pack(
                    'HHHH',
                    self.term_size['height'], self.term_size['width'],
                    self.term_size['pixelheight'], self.term_size['pixelwidth'])
            )
        except Exception as exc:
            log.error('ioctl windows size error: {}'.format(traceback.print_exc()))
            return

        # noinspection PyBroadException
        try:
            cmd = [config.python_path, '-m', 'relay.SSH_Client']
            log.debug('cmd: {} {} {}'.format(cmd, str(self.terminal_audit.tunnel_info), str(self.term_env)))

            self.proc = subprocess.Popen(
                [cmd[0], cmd[1], cmd[2], str(self.terminal_audit.tunnel_info), str(self.term_env)],
                stdin=self.slave, stdout=self.slave, stderr=self.slave,
                start_new_session=True,
                close_fds=True,
            )

            # Important.the parent thread must close slave pty.
            os.close(self.slave)

        except Exception as exc:
            log.error('exec subprocess error: {}'.format(traceback.print_exc()))
            return
