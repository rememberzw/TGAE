# TGAE
tunnel gateway audit engine

tunnel info JSON:

'{"usess":{"uid":"zhouwei","uname":"gudao","sid":"123456qwerty","rip":"127.0.0.1"},"res":{"proto":"ssh","dip":"10.25.5.2","dp":22,"acc":"zhouwei","pw":"123456","su":"","supw":"","ctlint":"ctrl+c","to":10},"cmdlist":{"type":"b","level":0,"policy":0/1/2/3,"list":["123","456"]}}'

tunnel info DICT:

{
    'usess': {'uid': 'zhouwei', 'uname': 'gudao', 'sid': '123456qwerty', 'rip': '127.0.0.1'},
    'res': {'proto': 'ssh', 'dip': '10.25.5.2', 'dp': 22, 'acc': 'zhouwei', 'pw': '123456', 'su': '', 'supw': '', 'ctlint': 'ctrl+c', 'to': 10},
    'nxres': {},
    'cmdlist': {
        'type': 'b',
        'level': 0,
        'policy': 3,
        'list':
            ['123', '456']
    }
}

VG9tJkplcnJ5

usess：用户会话
    uid：主账号
    sid：会话id
    rip：真实客户端IP

res：资源信息
    proto：登录协议
    dip：目标IP
    dp：目标端口
    acc：从账号
    pw：密码
    su：su命令，如没有则留空
    supw：su密码，如没有则留空
    nxres：第二跳资源信息，内容跟res相同，如没有则留空
 
cmdlist：黑白名单，如没有则留空
    type：名单类型：b:黑，w:白。互斥。
    level: 名单等级
    policy: 名单策略--0:不阻断不告警，1：阻断不告警，2：不阻断但告警，3:阻断并告警
    list：名单列表




