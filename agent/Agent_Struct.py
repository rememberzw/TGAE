import logging

log = logging.getLogger('agent')

LOG_TYPE = {
    'stream': {
        'type': '0x27',
        'start': '0x01',
        'end': '0x02',
    },
    'warn': {
        'type': '0x26',
        'sensitive_oper': '0x01',
    }
}


class AgentStruct:
    def __init__(self):
        # term or sterm
        self._topic = None

        # user_id
        self.uid = None
        # user_name
        self.uname = None
        # session_id
        self.sid = None

        # user_addr
        self.sip = None
        # user_port
        self.sport = 0
        # resource_addr
        self.dip = None
        # resource_port
        self.dport = 0

        self.rip = None
        # resource_account
        self.acc = None

        self.flag = 0
        # log_time
        self.optime = None
        self.endtime = None
        self.opsn = 0
        self.oper = None
        # clean oper
        self.content = None
        # success or failed
        self.rst = None

        self.version = 1
        self.log_type = None
        self.log_subtype = None
        self.dev_name = None
        self.dev_ipv4 = None
        self.dev_ipv6 = None
        self.login_action = 0
        self.login_type = None
        self.access_id = None
        self.resource_name = None
        self.resource_account_type = None
        self.tool_name = None


class AgentStructWarn:
    def __init__(self):
        self._topic = 'warn'
        self.session_id = None

        self.uid = None
        self.uname = None
        self.sid = None

        self.sip = None
        self.sport = 0
        self.dip = None
        self.dport = 0

        self.rip = None
        self.acc = None

        self.optime = None
        self.opsn = 0
        # eg: rm /tmp/lse.log
        self.content = None
        self.level = 0

        self.act = 'DENY'
        self.aty = '违规操作'
