import pexpect

# python_path = '/opt/somf/python-somf/bin/python3'
python_path = 'python3'

# enable REST API
channel_request = 'no'
request_timeout = 5

# ssh server
sshd_ip = ''
sshd_port = 9022

# agent es or kafka
agent_executor_num = 3
agent_mode = 'es'

# kafka
kafka_server = '10.11.21.2'
stream_topic = 'mssh'
oper_topic = 'ssh'
warn_topic = 'warn'

# manage
manage_port = 9025

# ssh client
login_prompt = [
        '[lL]ogin:',
        '[uU]sername:',
        'login name:'
        ]

passwd_prompt = [
        '[pP]assword:'
        ]

shell_prompt = [
        '\$',
        '#',
        '>'
        ]

failed_prompt = [
        pexpect.EOF,
        pexpect.TIMEOUT,
        'incorrect password',
        'Authentication failure',
        'Permission denied',
        '\sdoes not exist',
        '\sNo route to host',
        'Login incorrect'
        ]

ssh_first_connect_prompt = [
        'Are you sure you want to continue connecting'
        ]

ctlint = {
        'ctrl+c': b'\x03',
        'ctrl+d': b'\x04',
        'ctrl+x': b'\x18',
        'ctrl+y': b'\x19',
        # 'ctrl+y': b'\x1a'
        }
