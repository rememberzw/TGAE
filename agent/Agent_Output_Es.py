import sys
import time
import logging

from elasticsearch import Elasticsearch

from etc import config

log = logging.getLogger('agent')


class AgentOutput:
    def __init__(self):
        # noinspection PyBroadException
        try:
            self.es_server = config.es_server
            self.index_type = config.index_type
            self.es = None
        except Exception as exc:
            log.error('init error: {}'.format(exc))

    def init_es(self):
        # noinspection PyBroadException
        try:
            log.info('init es.')
            self.es = Elasticsearch(config.es_server)
        except Exception as exc:
            log.error('init es error: {}'.format(exc))
            sys.exit(1)

    def create_index(self, _index):
        # noinspection PyBroadException
        try:
            _index = self.format_index(_index)
            log.info('create index: {}'.format(_index))
            if self.es.indices.exists(index=_index) is not True:
                res = self.es.indices.create(index=_index, ignore=400)
                log.info('create index success: {}'.format(res))
            else:
                log.info('{} is already exists.'.format(_index))
        except Exception as exc:
            log.error('create index error: {}'.format(exc))
            sys.exit(1)

    def index_data(self, _index, _id, data):
        # noinspection PyBroadException
        try:
            _index = self.format_index(_index)
            log.debug('index data: {}:{}'.format(_index, data))
            if (config.index_stream in _index) and (_id is not None):
                self.es.index(index=_index, doc_type=self.index_type, id=_id, body=data)
            else:
                self.es.index(index=_index, doc_type=self.index_type, body=data)
        except Exception as exc:
            log.error('index data error: {}'.format(exc))

    @staticmethod
    def format_index(_index):
        return _index + time.strftime("%Y%m", time.localtime())
