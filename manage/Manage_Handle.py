import logging

log = logging.getLogger('manage')


class ManageHandle:
    def __init__(self, onlines):
        self.useage = '''\nUsage:\n
Options:
    help    - show this help message and exit
    online  - Print online information for all connections
'''
        self.onlines = onlines

    def handle_input(self, cmd):
        log.debug('cmd: {}'.format(cmd))
        info = ''
        if cmd == 'online':
            num = 0
            debug = ''
            for pid in self.onlines:
                num += 1
                debug += '{} --- {}\r\n'.format(pid, self.onlines.get(pid))
            info += '\r\nTotal: {:d}\r\n{}'.format(num, debug)
            return info

        elif cmd == 'help':
            return self.useage

        else:
            return self.useage
