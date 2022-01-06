import logging

log = logging.getLogger('agent')

LOG_TYPE = {
    'stream': {
        'type': '0x27',
        'start': '0x01',
        'start_desc': '会话开始',
        'end': '0x02',
        'end_desc': '会话结束',
        'oper': '0x03',
        'oper_desc': '会话操作',
    },
    'warn': {
        'type': '0x26',
        'sensitive_oper': '0x01',
        'sensitive_oper_desc': '高风险操作',
    }
}

LOGIN_TYPE = {
    'ssh': 1,
    'SSH': 1,
    'telnet': 2,
    'Telnet': 2,
}

LOGIN_TYPE_NAME = {
    1: 'ssh',
    2: 'telnet',
}

END_REASON = {
    'normal_exit': 1,
    'command_exit': 2,
    'admin_exit': 3,
    'login_error': 4,
}

END_REASON_DESC = {
    1: '正常结束',
    2: '命令规则阻断',
    3: '管理员人工阻断',
    4: '登录资源失败',
}

OPER_ACTION = {
    "sensitive:-1": 1,
    "illegal:0": 2,
    "illegal:1": 3,
    "treasury:allow=-1": 5,
    "treasury:deny=0": 6,
    "treasury:timeout=0": 7,
    "treasury:timeout=1": 8,
    "cancel:0": 9,
}

OPER_ACTION_DESC = {
    1: '敏感指令执行',
    2: '指令阻断',
    3: '会话阻断',
    5: '申请被批准',
    6: '申请被拒绝',
    7: '申请超时（指令阻断）',
    8: '申请超时（会话阻断）',
    9: '取消'
}


class AgentStruct:
    def __init__(self):
        # term or sterm
        self._topic = None
        self.session_type = None

        self.version = 1
        self.access_id = None
        # session_id
        self.session_id = None

        self.log_type = None
        self.log_subtype = None
        self.log_subtype_desc = None

        self.resource_name = None
        self.resource_department = None
        self.resource_type = None

        # user_id
        self.user_id = None
        # user_name
        self.user_name = None
        self.user_department = None

        self.login_action = 0
        self.login_type = None
        self.login_type_name = None

        # user_addr
        self.user_addr = None
        # user_port
        self.user_port = 0
        # resource_addr
        self.resource_addr = None
        # resource_port
        self.resource_port = 0
        # resource_account
        self.resource_account = None
        self.resource_account_type = None
        self.tool_name = None

        # log_time
        self.log_time = None
        self.end_time = None
        self.duration = 0
        self.end_reason = None
        self.end_reason_desc = None

        self.dev_name = None
        self.dev_ipv4 = None
        self.dev_ipv6 = None

        self.rip = None

        self.operate = None
        self.object = None
        # success or failed
        self.result = None
        self.flag = 0
        self.sequence = 0
        self.content = None
        # clean oper
        self.clean_content = None
        self.level = None
        self.level_name = None


class AgentStructWarn:
    def __init__(self):
        self._topic = None

        self.version = 1
        self.log_type = None
        self.log_subtype = None
        self.log_subtype_desc = None

        self.log_time = None
        self.dev_name = None
        self.dev_ipv4 = None
        self.dev_ipv6 = None
        self.session_id = None

        self.action_id = 0
        self.action_desc = None
        self.approvers = None
        self.operate_content = None

        self.user_id = None
        self.user_name = None
        self.user_addr = None

        self.flag = 0
        self.sequence = 0

        self.resource_addr = None
        self.resource_port = 0
        self.resource_account = None


class AgentStructSomf:
    def __init__(self):
        self._topic = None

        self.id = None
        self.session_id = None
        self.access_id = None
        self.treasury_id = None

        self.user_id = None
        self.user_name = None
        self.user_department = None

        self.log_time = None

        self.user_addr = None
        self.log_type = None
        self.log_subtype = None
        self.log_subtype_desc = None

        self.operate = None
        self.object = None
        self.result = None
        self.content = None
