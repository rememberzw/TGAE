import queue
import json
import threading
import logging

from agent import Agent_Output_Kafka

log = logging.getLogger('agent')


class AgentProcess:
    def __init__(self, my_loop, agent_queue):
        # noinspection PyBroadException
        try:
            self.agent_output = Agent_Output_Kafka.AgentOutput()
            self.agent_output.agent_init()

            self.my_loop = my_loop
            self.agent_queue = agent_queue
            self.lock = threading.Lock()
            self.count = 0
            self.END = False
        except Exception as exc:
            log.error('Init error: {}'.format(exc))

    def start(self):
        log.info('Running...')
        total = 0
        while not self.END or not self.agent_queue.empty():
            # noinspection PyBroadException
            try:
                record = self.agent_queue.get(timeout=1)
                self.agent_queue.task_done()
                # log.debug('***record: {}'.format(json.dumps(record.__dict__)))
            except queue.Empty:
                continue
            except Exception as exc:
                log.error('Get from queue error: {}'.format(exc))
                break

            # noinspection PyBroadException
            try:
                _topic = record.__dict__.pop('_topic')
                record_json = json.dumps(record.__dict__)
            except Exception as exc:
                log.error('Convert dict to json error: {}'.format(exc))
                continue

            try:
                self.agent_output.agent_send(_topic, record_json)
            except Exception as exc:
                log.error('agent send error: {}'.format(exc))

            self.lock.acquire()
            self.count = self.count + 1
            self.lock.release()
            total = total + 1

        log.info('each record: {:d}'.format(int(total)))

    def finish(self):
        log.info('finish and record count all: {:d}'.format(self.count))
        # self.agent_output.close_kafka()
