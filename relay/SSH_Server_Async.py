import sys
import asyncssh
import logging
import functools

from relay.SSH_Server import MySSHServer
from etc import config

log = logging.getLogger('relay')


class MySSHServerAsync:
    def __init__(self, loop, agent_queue, onlines):
        self.loop = loop
        self.agent_queue = agent_queue
        self.onlines = onlines

    async def start(self):
        log.info('localhost:{:d} is running...'.format(config.sshd_port))
        # noinspection PyBroadException
        try:
            myserver = await asyncssh.create_server(
                functools.partial(MySSHServer, self.loop, self.agent_queue, self.onlines),
                config.sshd_ip,
                config.sshd_port,
                server_host_keys=['relay/ssh_host_rsa_key'],
                line_editor=False,
                encoding=None
                    )
        except Exception as exc:
            log.error('create server error: {}'.format(exc))
            sys.exit(1)
