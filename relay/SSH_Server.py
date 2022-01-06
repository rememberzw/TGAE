import os
import sys
import time
import threading
import logging
import traceback
import selectors

import paramiko

from relay.SSH_Channel import SSHChannel
from lib.Terminal_Audit import TerminalAudit
from lib import func_collection
from etc import config

log = logging.getLogger('paramiko')


class ConnHandlerThd(threading.Thread):
    def __init__(self, conn, address, keyfile, agent_queue, onlines):
        # noinspection PyBroadException
        try:
            threading.Thread.__init__(self)
            self.conn = conn
            self.address = address
            self.keyfile = 'relay/' + keyfile
            self.agent_queue = agent_queue
            self.onlines = onlines

            self.client_channel = None
            self.server_channel = None

            self.keep_running = True
            self.end_reason = 'normal_exit'

            self.terminal_audit = TerminalAudit(self.agent_queue, self.onlines)
            self.terminal_audit.ast.user_addr = func_collection.ipv4_mapped(self.address[0])
            self.terminal_audit.ast.user_port = self.address[1]
            # log.debug(self.address)
            # log.debug(self.terminal_audit.ast.user_addr)
            # log.debug(self.terminal_audit.ast.user_port)
        except Exception as exc:
            log.error('init error:{}'.format(traceback.print_exc()))
            sys.exit(1)

    def run(self):
        log.info('session start...')
        host_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        transport = paramiko.Transport(self.conn, default_max_packet_size=config.max_psize)
        transport.add_server_key(host_key)

        self.server_channel = SSHChannel(self.terminal_audit)

        # noinspection PyBroadException
        try:
            transport.start_server(server=self.server_channel)
        except Exception as exc:
            log.error('start server error:{}'.format(traceback.print_exc()))

        self.client_channel = transport.accept()
        if self.client_channel is None:
            log.error('no channel.')
            return

        self.terminal_audit.client_channel = self.client_channel
        self.terminal_audit.oper_policy.client_channel = self.client_channel

        while not self.server_channel.master_pty_pipe:
            time.sleep(0.1)

        self.terminal_audit.onlines_control.add_online(self.ident, self.terminal_audit.tunnel_info)

        sel = selectors.DefaultSelector()
        sel.register(self.client_channel, selectors.EVENT_READ)
        sel.register(self.server_channel.master_pty_pipe, selectors.EVENT_READ)

        while self.keep_running:
            # noinspection PyBroadException
            try:
                for key, mask in sel.select(timeout=None):

                    if key.fileobj is self.client_channel:
                        data = self.client_channel.recv(config.max_psize)
                        if not data:
                            self.keep_running = False

                        log.debug('CLIENT> ({:d}) {}'.format(len(data), data))
                        res, action = self.terminal_audit.client_input(data)
                        if res:
                            os.write(self.server_channel.master, data)
                        else:
                            if action == '0':
                                os.write(self.server_channel.master, self.terminal_audit.ctlint)
                            else:
                                self.end_reason = 'command_exit'
                                self.keep_running = False

                    if key.fileobj is self.server_channel.master_pty_pipe:
                        data = self.server_channel.master_pty_pipe.read(config.max_psize)
                        if not data:
                            self.keep_running = False
                        log.debug('SERVER> ({:d}) {}'.format(len(data), data))
                        self.terminal_audit.server_output(data)
                        self.client_channel.sendall(data)

            except Exception as exc:
                log.error('select error: {}'.format(traceback.print_exc()))
                self.keep_running = False

        while transport.is_active():
            time.sleep(0.1)
            transport.close()

        self.client_channel.close()
        self.server_channel.proc.terminate()

        if self.terminal_audit.login_success:
            self.terminal_audit.stream_end(self.end_reason)

        self.terminal_audit.onlines_control.pop_online(self.ident)
