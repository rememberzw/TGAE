import sys
import socket
import queue
import optparse
import textwrap
import selectors
import logging.config

from etc import config
from relay import SSH_Server
from agent import Agent_Process
from manage import Manage_Server

logging.config.fileConfig('logging.config')
log = logging.getLogger('paramiko')

AGENT_QUEUE = queue.Queue()
AGENT_LIST = list()
AGENT_COUNT = 0
ONLINES = dict()

manage_server = Manage_Server.ManageServer(ONLINES)


def start_manage_server():
    manage_server.start()


def start_agent_process():
    for thread in range(config.agent_thread_num):
        agent_process = Agent_Process.AgentProcess(AGENT_QUEUE, AGENT_COUNT)
        AGENT_LIST.append(agent_process)
        agent_process.start()


def stop_agent_process():
    for agent in AGENT_LIST:
        agent.END = True
        agent.join()
        log.info('agent({}) is stop.'.format(agent.getName()))


def start_ssh_channel(host, port, keyfile):
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # noinspection PyBroadException
    try:
        server_socket.setblocking(False)
        server_socket.bind((host, port))
        server_socket.listen()
    except Exception as exc:
        log.error('server listen error:{}'.format(exc))
        stop_agent_process()
        return

    log.info('listening ({}):({})'.format(host, port))

    def accept(my_socket):
        conn, address = my_socket.accept()
        srv_thd = SSH_Server.ConnHandlerThd(conn, address, keyfile, AGENT_QUEUE, ONLINES)
        srv_thd.setDaemon(True)
        srv_thd.start()

    sel = selectors.DefaultSelector()
    sel.register(server_socket, selectors.EVENT_READ, accept)
    while True:
        try:
            events = sel.select(1)
            for key, _ in events:
                key.data(key.fileobj)
        except KeyboardInterrupt:
            log.info('sshd_channel stop.')
            stop_agent_process()
            manage_server.keep_running = False
            return


def setup_sshd_channel():
    usage = """\
    usage: ssh server [options]
    """
    parser = optparse.OptionParser(usage=textwrap.dedent(usage))

    parser.add_option(
        '-H', '--host', dest='host', default=config.sshd_ip,
        help='listen on HOST [default: %default].')
    parser.add_option(
        '-P', '--port', dest='port', type='int', default=config.sshd_port,
        help='listen on PORT [default: %default].'
        )
    parser.add_option(
        '-K', '--keyfile', dest='keyfile', metavar='FILE', default=config.sshd_keyfile,
        help='Path to private key [default: %default].'
        )

    options, args = parser.parse_args()

    if options.keyfile is None:
        parser.print_help()
        sys.exit(-1)

    return options


def start():
    start_manage_server()
    start_agent_process()
    options = setup_sshd_channel()
    start_ssh_channel(options.host, options.port, options.keyfile)


if __name__ == '__main__':
    start()
