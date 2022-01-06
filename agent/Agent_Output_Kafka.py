import logging
from kafka import KafkaProducer
from etc import config

log = logging.getLogger('agent')


class AgentOutput:
    def __init__(self):
        # noinspection PyBroadException
        try:
            self.kafka_server = config.kafka_server
            self.stream = config.stream_topic
            self.oper = config.oper_topic
            self.warn = config.warn_topic

            self.producer = None
        except Exception as exc:
            log.error('init error: {}'.format(exc))

    def agent_init(self):
        # noinspection PyBroadException
        try:
            log.info('agent init...')
            self.producer = KafkaProducer(bootstrap_servers=self.kafka_server)
        except Exception as exc:
            log.error('agent init error: {}'.format(exc))

    def agent_send(self, _topic, data):
        # noinspection PyBroadException
        try:
            if self.producer:
                log.debug('***send: ({}):{}'.format(_topic, data))
                self.producer.send(_topic, data.encode())
            else:
                self.agent_init()
        except Exception as exc:
            log.error('agent send error: {}'.format(exc))
