import sys
import socket
import selectors
import threading
import logging

from manage import Manage_Handle
from etc import config

log = logging.getLogger('manage')


class ManageServer(threading.Thread):
    def __init__(self, onlines):
        # noinspection PyBroadException
        try:
            threading.Thread.__init__(self)
            self.manage_handle = Manage_Handle.ManageHandle(onlines)
            self.keep_running = True
            self.sel = None
        except Exception as exc:
            log.error('init error: {}'.format(exc))
            sys.exit(1)

    def run(self):
        server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # noinspection PyBroadException
        try:
            server_socket.setblocking(False)
            server_socket.bind((config.sshd_ip, config.manage_port))
            server_socket.listen()
        except Exception as exc:
            log.error('manage_server listen error:{}'.format(exc))
            return

        log.info('manage_server listening ({}):({})'.format(config.sshd_ip, config.manage_port))

        self.sel = selectors.DefaultSelector()
        self.sel.register(server_socket, selectors.EVENT_READ, self.accept)
        while self.keep_running:
            try:
                events = self.sel.select(1)
                for key, _ in events:
                    key.data(key.fileobj)
            except KeyboardInterrupt:
                log.info('manage_server stop.')
                break

        self.sel.close()
        log.info('manage_server stop.')

    def accept(self, my_socket):
        new_conn, address = my_socket.accept()
        new_conn.setblocking(False)
        self.sel.register(new_conn, selectors.EVENT_READ, self.read)

    def read(self, conn):
        client_address = conn.getpeername()
        data = conn.recv(config.max_psize)
        if data:
            log.info('manage_server received: {}: {}'.format(client_address, data))
            recv = self.manage_handle.handle_input(data.decode())
            conn.sendall(recv.encode())
        else:
            self.sel.unregister(conn)
            conn.close()

