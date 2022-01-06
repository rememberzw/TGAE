import sys
import logging
from socket import *

from etc import config

log = logging.getLogger('manage')


class ManageClient:
    def __init__(self):
        pass

    @staticmethod
    def manage_client(cmd):
        try:
            client = socket(AF_INET, SOCK_STREAM)
        except Exception as exc:
            print('failed to create socket: {}'.format(exc))
            sys.exit(1)

        address = None
        try:
            address = (config.sshd_ip, config.manage_port)
            client.connect(address)
        except Exception as exc:
            print('failed to connect server({}): {}\r\nSSH server is not running.'.format(str(address), exc))
            sys.exit(1)

        try:
            client.sendall(cmd.encode())
            recv = client.recv(1024).decode()
            print(recv)
        except Exception as exc:
            log.error('send message failed: {}'.format(exc))
            sys.exit(1)
