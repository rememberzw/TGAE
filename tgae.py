import sys
import os
import signal
import functools
import concurrent.futures
import queue
import asyncio
import traceback
import logging.config

from relay import SSH_Server_Async
from agent import Agent_Process
from manage import Manage_Interface
from etc import config

logging.config.fileConfig('logging.config')
log = logging.getLogger('relay')

# ----init----
MY_PID = os.getpid()

MY_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(MY_LOOP)

AGENT_QUEUE = queue.Queue()

ONLINES = {}

SSH_SERVER = SSH_Server_Async.MySSHServerAsync(MY_LOOP, AGENT_QUEUE, ONLINES)
AGENT_PROCESS = Agent_Process.AgentProcess(MY_LOOP, AGENT_QUEUE)
MANAGE_INTERFACE = Manage_Interface.ManageInterface(MY_LOOP, ONLINES)

EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=None)
BLOCKING_TASKS = [
        MY_LOOP.run_in_executor(EXECUTOR, AGENT_PROCESS.start)
        for i in range(config.agent_executor_num)
        ]


async def wait_executor(blocking_tasks):
    # completed, pending = await asyncio.wait(blocking_tasks)
    await asyncio.wait(blocking_tasks)
    log.info('executor is completed')


def agent_process_start():
    # noinspection PyBroadException
    try:
        # [ log.debug('Agent_Process blocking task:{}'.format(task)) for task in blocking_tasks ]
        asyncio.ensure_future(wait_executor(BLOCKING_TASKS))
    except Exception as exc:
        log.error('Agent_Process start error: {}'.format(exc))
        sys.exit(1)


def manage_interface_start():
    # noinspection PyBroadException
    try:
        mi_future = asyncio.ensure_future(MANAGE_INTERFACE.start())
    except Exception as exc:
        log.error('Manage_Interface start error: {}'.format(exc))
        sys.exit(1)


def ssh_call_back(ssh_future):
    signal_handler()
    # [ log.debug('ssh_call_back all task: {}'.format(task)) for task in asyncio.Task.all_tasks() ]


def ssh_server_start():
    # noinspection PyBroadException
    try:
        ssh_future = asyncio.ensure_future(SSH_SERVER.start())
        ssh_future.add_done_callback(ssh_call_back)
    except Exception as exc:
        log.error('SSH_Server start error: {}'.format(exc))
        sys.exit(1)


def ask_exit(signame):
    log.info("got signal: {}".format(signame))

    # noinspection PyBroadException
    try:
        for pid in ONLINES:
            log.info('SSH_Server exit pid: {}'.format(pid))
            os.killpg(pid, signal.SIGTERM)
    except Exception as exc:
        log.error('SSH_Server exit pid error: {}'.format(exc))

    # noinspection PyBroadException
    try:
        AGENT_PROCESS.END = True
        for task in BLOCKING_TASKS:
            # log.info('start cancel blocking task: {}'.format(task))
            if task.cancelled():
                log.debug('blocking task is canceled')
            elif task.done():
                log.debug('blocking task is done')
            else:
                log.debug('try to cancel blocking task.')
                task.cancel()
    except Exception as exc:
        log.error('cancel blocking task error: {}'.format(exc))
    finally:
        AGENT_PROCESS.finish()

    # noinspection PyBroadException
    try:
        [log.info('cancel task: {}, {}'.format(task, task.cancel())) for task in asyncio.all_tasks()]
    except Exception as exc:
        log.error('Ask_Exit task cancel error: {}'.format(exc))

    # noinspection PyBroadException
    try:
        MY_LOOP.stop()
    except Exception as exc:
        log.error('stop loop error: {}'.format(exc))
    finally:
        # kill_cmd = 'kill -9 ' + str(mypid)
        # log.info('{}'.format(kill_cmd))
        # # os.system(kill_cmd)
        log.info('SSH Server has stopped.')


def signal_handler():
    # noinspection PyBroadException
    try:
        for signame in ('SIGINT', 'SIGTERM'):
            MY_LOOP.add_signal_handler(getattr(signal, signame), functools.partial(ask_exit, signame))
    except Exception as exc:
        log.error('add signal error: {}'.format(exc))


def start():
    agent_process_start()
    manage_interface_start()
    ssh_server_start()


if __name__ == '__main__':

    start()

    # noinspection PyBroadException
    try:
        MY_LOOP.run_forever()
    except Exception:
        log.error('run forever error: {}'.format(traceback.print_exc()))
