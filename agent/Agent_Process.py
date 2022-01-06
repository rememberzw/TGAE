import queue
import json
import threading
import logging
from etc import config

if config.agent_mode == 'kafka':
    from agent.Agent_Output_Kafka import AgentOutput
else:
    from agent.Agent_Output_Es import AgentOutput

log = logging.getLogger('agent')


class AgentProcess(threading.Thread):
    def __init__(self, agent_queue, agent_count):
        # noinspection PyBroadException
        try:
            threading.Thread.__init__(self)
            self.lock = threading.Lock()

            self.agent_queue = agent_queue
            self.count = agent_count
            self.END = False

            self.agent_output = AgentOutput()
            self.agent_output.agent_init()

        except Exception as exc:
            log.error('Init error: {}'.format(exc))

    def run(self):
        log.info('{} Running...'.format(self.getName()))
        total = 0
        while not self.END or not self.agent_queue.empty():
            # noinspection PyBroadException
            try:
                record = self.agent_queue.get(timeout=1)
                self.agent_queue.task_done()
                # log.debug('******record: {}'.format(record.__dict__))
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

            # noinspection PyBroadException
            try:
                self.agent_output.agent_send(_topic, record_json)
            except Exception as exc:
                log.error('Agent send error: {}'.format(exc))

            self.lock.acquire()
            self.count = self.count + 1
            self.lock.release()
            total = total + 1

        log.info('Each record: {:d}'.format(int(total)))

    def finish(self):
        log.info('Finish and record count all: {:d}'.format(self.count))
