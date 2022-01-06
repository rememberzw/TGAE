import asyncssh
import logging

from relay.SSH_Server_Session import MySSHServerSession
from lib import Terminal_Audit
from lib import Channel_Request
from etc import config

log = logging.getLogger('relay')


class MySSHServer(asyncssh.SSHServer):
    def __init__(self, myloop, agent_queue, onlines):
        try:
            asyncssh.SSHServer.__init__(self)
            self.myloop = myloop
            self.agent_queue = agent_queue
            self.terminal_audit = Terminal_Audit.TerminalAudit(agent_queue, onlines)
        except Exception as exc:
            log.error('init error: {}'.format(exc))

    def connection_made(self, conn):
        try:
            peername = conn.get_extra_info('peername')
            self.terminal_audit.ast.sip = peername[0]
            self.terminal_audit.ast.sport = peername[1]
            log.debug('connection_made received from ({}:{})'.format(
                self.terminal_audit.ast.sip, self.terminal_audit.ast.sport))
        except Exception as exc:
            log.error('connection_made error: {}'.format(exc))

    def connection_lost(self, exc):
        try:
            if exc:
                log.debug('connection error: {}'.format(exc))
            else:
                log.debug('connection closed.')
        except Exception as exc:
            log.error('connection_lost error: {}'.format(exc))

    def begin_auth(self, username):
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        try:
            log.debug('validate_password username={}, password={}'.format(username, password))

            if config.channel_request == 'yes':
                channel_request = Channel_Request.ChannelRequest(username, password)
                result, tunnel_json = channel_request.get_channel()
                if not result:
                    return False
                else:
                    username = tunnel_json
                    password = 'VG9tJkplcnJ5'

            if self.terminal_audit.process_tunnel_info(username, password):
                return True
            else:
                return False
        except Exception as exc:
            log.error('connection made error: {}'.format(exc))

    def session_requested(self):
        try:
            log.debug('session_requested start')
            return MySSHServerSession(self.myloop, self.terminal_audit)
        except Exception as exc:
            log.error('session_requested error: {}'.format(exc))
