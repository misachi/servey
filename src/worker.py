import os
import signal
import errno


class Worker:
    def __init__(self, sock, ppid, config) -> None:
        self.worker_id = os.getpid()
        self.parent_id = ppid
        self.cfg = config
        self.log = config.log
        self.sock = sock
    
    def sigterm_handler(self):
        pass

    def sigint_handler(self, sig_num, frame):
        self.log.info('[{}] is shutting down'.format(os.getpid()))
        os._exit(1)
    
    def init_signals(self):
        signal.signal(signal.SIGINT, self.sigint_handler)

    def process_request(self):
        pass

    def run(self):
        self.sock.listen(self.cfg.queue)
        self.log.debug('Waiting for connection...')
        self.init_signals()
        while True:
            try:
                conn, addr = self.sock.accept()
            except OSError as e:
                if e.errno not in [errno.EWOULDBLOCK, errno.EAGAIN]:
                    raise
                continue

            self.log.debug('Accepted connection: {} from {}'.format(addr, self.worker_id))

            n = conn.send(b'\r\nContent-Type: text/plain; Hello World')
            if n != len('\r\nContent-Type: text/plain; Hello World'):
                self.log.debug('Unable to send data')
                raise Exception('Something bad has happened')
            self.log.debug('Message sent')
