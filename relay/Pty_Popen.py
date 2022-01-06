import os
import pty


class PtyPopen:
    def __init__(self, command, *args):
        self.args = args
        self.max_read = 1024
        # self.delay = 0
        # Clone this process in a separate thread.
        self.pid, self.fd = pty.fork()
        # In the child process, pid will contain 0. In the parent,
        # it will contain the pid of the child.
        # In the child process, so replace the python
        if self.pid == 0:
            # process with the requested command.
            # os.execv (command, [''] + args)
            # os.execlp(command, 'CommandChannel', args[0], args[1], args[2], args[3])
            os.execlp(command, 'CommandChannel', *args)
        # In the parent process, which stays live
        else:
            pass

    def get_args(self):
        return self.args

    def fileno(self):
        return self.fd

    # Do no need waitpid(), because pty_popen had do it.
    def close(self):
        # pyt.kill()
        # pty.wait()
        pass

    def read(self):
        return os.read(self.fd, self.max_read)

    def write(self, text):
        return os.write(self.fd, text)

    def writeall(self, text):
        total = len(text)
        sended = 0
        while sended < total:
            i = os.write(self.fd, text[sended:])
            if i > 0:
                sended = sended + i
