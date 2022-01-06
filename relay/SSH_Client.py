import sys
import os
import time
import traceback
import getpass
import pexpect
import struct
import fcntl
import termios
import signal

from etc import config


class SSHClient:
    def __init__(self, tunnel_info, term_env):
        self.child = None
        self.protocol = None
        self.ip = None
        self.port = None
        self.account = None
        self.passwd = None
        # self.ctlint = None
        self.timeout = None
        self.su = None
        self.supw = None

        self.nx_res_info = None
        self.nx_protocol = None
        self.nx_ip = None
        self.nx_port = None
        self.nx_account = None
        self.nx_passwd = None
        # self.nx_ctlint = None
        self.nx_timeout = None
        self.nx_su = None
        self.nx_supw = None

        self.parse_tunnel_info(eval(tunnel_info))

        if eval(term_env).get('LANG'):
            os.environ['LANG'] = eval(term_env).get('LANG')
        if eval(term_env).get('LC_CTYPE'):
            os.environ['LC_CTYPE'] = eval(term_env).get('LC_CTYPE')
        if eval(term_env).get('TERM'):
            os.environ['TERM'] = eval(term_env).get('TERM')

    def parse_tunnel_info(self, tunnel_info):
        # noinspection PyBroadException
        try:
            res_info = tunnel_info.get('res')
            self.protocol = str(res_info.get('proto'))
            self.ip = str(res_info.get('dip'))
            self.port = str(res_info.get('dp'))
            self.account = str(res_info.get('acc'))
            self.passwd = str(res_info.get('pw'))
            # self.ctlint = str(res_info.get('ctlint'))
            self.timeout = int(res_info.get('to'))

            self.su = res_info.get('su')
            if self.su:
                self.su = str(self.su)
                self.supw = res_info.get('supw')
                if self.supw:
                    self.supw = str(self.supw)
                else:
                    print('Miss the password of su.')
                    sys.exit(1)

            self.nx_res_info = tunnel_info.get('nxres')
            if self.nx_res_info:
                self.nx_protocol = str(self.nx_res_info.get('proto'))
                self.nx_ip = str(self.nx_res_info.get('dip'))
                self.nx_port = str(self.nx_res_info.get('dp'))
                self.nx_account = str(self.nx_res_info.get('acc'))
                self.nx_passwd = str(self.nx_res_info.get('pw'))
                # self.nx_ctlint = str(nx_res_info.get('ctlint'))
                self.nx_timeout = str(self.nx_res_info.get('to'))

                self.nx_su = self.nx_res_info.get('su')
                if self.nx_su:
                    self.nx_su = str(self.nx_su)
                    self.nx_supw = self.nx_res_info.get('supw')
                    if self.nx_supw:
                        self.nx_supw = str(self.nx_supw)
                    else:
                        print('Miss the password of su.')
                        sys.exit(1)

        except Exception as exc:
            print('Parse tunnel info error !')
            print(exc)
            sys.exit(1)

    def sigterminate_passthrough(self, sig, data):
        # In the parent process, which stays live
        try:
            print('SIGTERMINATE')
            if self.child is not None:
                self.child.sendeof()
                time.sleep(1)
                self.child.close(force=True)

            time.sleep(1)
            sys.exit(1)
        except Exception as exc:
            print(exc)

    def sigwinch_passthrough(self, sig, data):
        try:
            if os.isatty(1):
                s = struct.pack("HHHH", 0, 0, 0, 0)
                a = struct.unpack('hhhh', fcntl.ioctl(1, termios.TIOCGWINSZ, s))
                self.child.setwinsize(a[0], a[1])
        except Exception as exc:
            print(exc)

    def expect_connect(self):
        self.account = self.username_prompt(self.account)
        self.passwd = self.password_prompt(self.passwd)
        if (self.protocol == 'telnet') or (self.protocol == 'Telnet'):
            cmd = 'telnet ' + self.ip + ' ' + self.port
            print('(1.TGAE) {}'.format(cmd))
            if self.telnet_connect(cmd, 0):
                self.process_su_or_nx()

                print('(TGAE) into interactive mode.', end='')
                self.child.interact()

            self.child.close(force=True)
            sys.exit(1)

        elif (self.protocol == 'ssh') or (self.protocol == 'SSH'):
            cmd = 'ssh ' + self.ip + ' -l ' + self.account + ' -p ' + self.port
            print('(1.TGAE) {}'.format(cmd))
            if self.ssh_connect(cmd, 0):
                self.process_su_or_nx()

                print('(TGAE) into interactive mode.', end='')
                self.child.interact()

            self.child.close(force=True)
            sys.exit(1)

        else:
            print('Unkown protocol ({})'.format(self.protocol))
            sys.exit(1)

    def process_su_or_nx(self):
        if self.su and self.supw:
            if not self.exec_su(0):
                self.child.close(force=True)
                sys.exit(1)

        if self.nx_res_info:
            self.nx_account = self.username_prompt(self.nx_account)
            self.nx_passwd = self.password_prompt(self.nx_passwd)
            if (self.nx_protocol == 'telnet') or (self.nx_protocol == 'Telnet'):
                cmd = 'telnet ' + self.nx_ip + ' ' + self.nx_port
                print('(7.TGAE) {}'.format(cmd))
                if self.telnet_connect(cmd, 1):
                    if self.nx_su and self.nx_supw:
                        if not self.exec_su(1):
                            self.child.close(force=True)
                            sys.exit(1)
                else:
                    self.child.close(force=True)
                    sys.exit(1)

            elif (self.nx_protocol == 'ssh') or (self.nx_protocol == 'SSH'):
                cmd = 'ssh ' + self.nx_ip + ' -l ' + self.nx_account + ' -p ' + self.nx_port
                print('(7.TGAE) {}'.format(cmd, 1))
                if self.ssh_connect(cmd, 1):
                    if self.nx_su and self.nx_supw:
                        if not self.exec_su(1):
                            self.child.close(force=True)
                            sys.exit(1)
                else:
                    self.child.close(force=True)
                    sys.exit(1)

        return True

    def exec_su(self, flag):
        try:
            self.child.sendline((flag == 0) and self.su or self.nx_su)

            index = self.child.expect(
                config.failed_prompt +
                config.passwd_prompt +
                config.shell_prompt,
                searchwindowsize=5
            )
            print('(5.TGAE) {}{} '.format(self.child.before, self.child.after), end='')

            if index in range(
                    len(config.failed_prompt),
                    len(config.failed_prompt + config.passwd_prompt)
            ):
                self.child.sendline((flag == 0) and self.supw or self.nx_supw)

                index = self.child.expect(
                    config.failed_prompt +
                    config.shell_prompt,
                    searchwindowsize=5)
                print('(6.TGAE) {}{} '.format(self.child.before, self.child.after), end='')

                if index in range(
                        len(config.failed_prompt),
                        len(config.failed_prompt + config.shell_prompt)
                ):
                    return True

                else:
                    return False

            elif index in range(
                    len(config.failed_prompt + config.passwd_prompt),
                    len(config.failed_prompt + config.passwd_prompt + config.shell_prompt)
            ):
                return True

            else:
                return False

        except Exception as exc:
            print('Su execute error: {}'.format(exc))
            return False

    def telnet_connect(self, cmd, flag):
        try:
            if flag == 0:
                self.child = pexpect.spawnu(cmd)
                self.child.timeout = self.timeout
                # self.child.logfile = sys.stdout

                # register signal
                signal.signal(signal.SIGWINCH, self.sigwinch_passthrough)
                signal.signal(signal.SIGINT, self.sigterminate_passthrough)
                signal.signal(signal.SIGTERM, self.sigterminate_passthrough)
                self.sigwinch_passthrough(None, None)

            else:
                self.child.sendline(cmd)

            if ((flag == 0) and (self.account == 'noaccount_')) or \
                    ((flag == 1) and (self.nx_account == 'noaccount_')):
                index = len(config.failed_prompt) + 1
            else:
                index = self.child.expect(
                    config.failed_prompt +
                    config.login_prompt,
                    searchwindowsize=5
                )
                print('(2.TGAE) {}{} '.format(self.child.before, self.child.after))

            # time out
            if index in range(len(config.failed_prompt)):
                return False

            else:
                if ((flag == 0) and (self.account == 'noaccount_')) or \
                        ((flag == 1) and (self.nx_account == 'noaccount_')):
                    print('(2.TGAE) this device does not need an account.')
                else:
                    self.child.sendline((flag == 0) and self.account or self.nx_account)

                index = self.child.expect(
                    config.failed_prompt +
                    config.passwd_prompt,
                    searchwindowsize=5
                )
                print('(3.TGAE) {}{} '.format(self.child.before, self.child.after))

                if index in range(
                        len(config.failed_prompt),
                        len(config.failed_prompt + config.passwd_prompt)
                ):
                    self.child.sendline((flag == 0) and self.passwd or self.nx_passwd)

                    index = self.child.expect(
                        config.failed_prompt +
                        config.shell_prompt,
                        searchwindowsize=5)
                    print('(4.TGAE) {}{} '.format(self.child.before, self.child.after), end='')

                    if index in range(
                            len(config.failed_prompt),
                            len(config.failed_prompt + config.shell_prompt)
                    ):
                        return True
                    else:
                        return False

                else:
                    return False
        except Exception as exc:
            print('Telnet connect error: {}'.format(exc))
            return False

    def ssh_connect(self, cmd, flag):
        try:
            if flag == 0:
                self.child = pexpect.spawnu(cmd)
                self.child.timeout = self.timeout
                # self.child.logfile = sys.stdout

                # register signal
                signal.signal(signal.SIGWINCH, self.sigwinch_passthrough)
                signal.signal(signal.SIGINT, self.sigterminate_passthrough)
                signal.signal(signal.SIGTERM, self.sigterminate_passthrough)
                self.sigwinch_passthrough(None, None)

            else:
                self.child.sendline(cmd)

            index = self.child.expect(
                config.failed_prompt +
                config.passwd_prompt +
                config.ssh_first_connect_prompt,
                searchwindowsize=-1
            )
            print('(2.TGAE) {}{} '.format(self.child.before, self.child.after))

            # time out
            if index in range(
                    len(config.failed_prompt)
            ):
                return False

            # SSH does not have the public key. Just accept it.
            elif index in range(
                    len(config.failed_prompt + config.passwd_prompt),
                    len(config.failed_prompt + config.passwd_prompt + config.ssh_first_connect_prompt)
            ):
                self.child.sendline('yes')

                index = self.child.expect(
                    config.failed_prompt +
                    config.passwd_prompt,
                    searchwindowsize=5)
                print('(3.TGAE) {}{} '.format(self.child.before, self.child.after))

            if index in range(
                    len(config.failed_prompt),
                    len(config.failed_prompt + config.passwd_prompt)
            ):
                self.child.sendline((flag == 0) and self.passwd or self.nx_passwd)

                index = self.child.expect(
                    config.failed_prompt +
                    config.shell_prompt,
                    searchwindowsize=5)
                print('(4.TGAE) {}{} '.format(self.child.before, self.child.after), end='')

                if index in range(
                        len(config.failed_prompt),
                        len(config.failed_prompt + config.shell_prompt)
                ):
                    return True

                else:
                    return False

            else:
                return False
        except Exception as exc:
            print('SSH connect error: {}'.format(exc))
            return False

    def username_prompt(self, account):
        if not account:
            num = 0
            while num < 3:
                print('Login: ', end='')
                # noinspection PyBroadException
                try:
                    account = input()
                except Exception:
                    print('You must enter the correct username.')
                    num = num + 1
                    continue

                if not account:
                    print('Account can not be None.')
                    num = num + 1
                    continue

                else:
                    return account

            # noinspection PyBroadException
            try:
                self.child.close(force=True)
            except Exception:
                pass

            sys.exit(1)

        else:
            return account

    def password_prompt(self, passwd):
        if not passwd:
            num = 0
            while num < 3:
                # noinspection PyBroadException
                try:
                    passwd = getpass.getpass()
                except Exception:
                    print('You must enter the correct password.')
                    num = num + 1
                    continue

                if not passwd:
                    print('Password can not be None.')
                    num = num + 1
                    continue

                else:
                    return passwd

            # noinspection PyBroadException
            try:
                self.child.close(force=True)
            except Exception:
                pass

            sys.exit(1)

        else:
            return passwd


if __name__ == '__main__':
    argv_len = len(sys.argv)
    if (argv_len != 2) and (argv_len != 3):
        print("Error: %s miss some argvs.\n" % sys.argv[0])
        sys.exit(1)

    my_tunnel_info = sys.argv[1]

    if argv_len == 3:
        my_term_env = sys.argv[2]
    else:
        my_term_env = str({'LANG': 'en_US.UTF-8', 'LC_CTYPE': 'en_US.UTF-8', 'TERM': 'xterm'})

    # noinspection PyBroadException
    try:
        ssh = SSHClient(my_tunnel_info, my_term_env)
        ssh.expect_connect()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
