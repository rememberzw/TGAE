import pexpect

# python_path = '/opt/somf/python-somf/bin/python3'
python_path = 'python3'

# enable REST API
channel_request = 'no'
request_timeout = 5

# ssh server
sshd_ip = ''
sshd_port = 9022
sshd_keyfile = 'ssh_host_rsa_key'
sshd_loglevel = 'INFO'

# max packet size
max_psize = 64*1024

# agent info
agent_thread_num = 5
agent_mode = 'kafka'

# kafka
kafka_server = '10.11.21.3:9092'
stream_topic = 'mssh'
oper_topic = 'ssh'
warn_topic = 'warn'
somf_topic = 'somf'

# manage
manage_port = 9025

# treasury info
treasury_request_url = 'http://10.3.0.86:20011/api/sf-pro/pro/getTreasuryStatus'
# treasury_request_url = 'http://10.11.21.2:9000/api/sf-pro/pro/getTreasuryStatus'
treasury_request_timeout = 5

# ssh client
login_prompt = [
        '[lL]ogin:',
        '[uU]sername:',
        'login name:',
        ]

passwd_prompt = [
        '[pP]assword:',
        ]

shell_prompt = [
        '\$',
        '#',
        '>',
        ']',
        ]

failed_prompt = [
        pexpect.EOF,
        pexpect.TIMEOUT,
        'incorrect password',
        'Authentication failure',
        'Permission denied',
        '\sdoes not exist',
        '\sNo route to host',
        'Login incorrect',
        ]

ssh_first_connect_prompt = [
        'Are you sure you want to continue connecting',
        ]

ctlint = {
        'ctrl+c': b'\x03',
        'ctrl+d': b'\x04',
        'ctrl+x': b'\x18',
        'ctrl+y': b'\x19',
        }

banner = '''                                    
,--------. ,----.     ,---.  ,------. 
'--.  .--''  .-./    /  O  \ |  .---' 
   |  |   |  | .---.|  .-.  ||  `--,  
   |  |   '  '--'  ||  | |  ||  `---. 
   `--'    `------' `--' `--'`------' 
'''