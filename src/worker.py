import os
import signal
import errno
import select

from _http.request import Request, RequestError


class Worker:
    def __init__(self, sock, ppid, config) -> None:
        self.worker_id = None
        self.parent_id = ppid
        self.cfg = config
        self.log = config.log
        self.sock = sock
    
    def sigquit_handler(self, sig_num, frame):
        self.sock.ensure_closed()
        os._exit(1)

    def sigint_handler(self, sig_num, frame):
        self.log.info('[{}] is shutting down'.format(os.getpid()))
        self.sock.ensure_closed()
        os._exit(1)
    
    def sigterm_handler(self, sig_num, frame):
        self.running = False
        os._exit(0)

    def init_signals(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGQUIT, self.sigquit_handler)
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def process_request(self, client_conn, client_addr):
        data = client_conn.recv(1024)
        try:
            req = Request(data)
        except RequestError as e:
            self.log.error('{}: {}'.format(e.error_code, e.args[0]))
            client_conn.send(bytes('HTTP/1.1 {} {}\r\n\r\n'.format(e.error_code, e.args[0]).encode('utf-8')))
            client_conn.close()
            return

    def run(self):
        self.sock.listen()
        self.log.debug('Waiting for connection...')
        self.worker_id = os.getpid()
        self.init_signals()

        while True:
            try:
                read = select.select([self.sock.sock], [], [], 1.1)
                if not read or (read and self.sock.sock not in read[0]):
                    continue
                client_conn, addr = self.sock.sock.accept()
                self.process_request(client_conn, addr)
            except OSError as e:
                if e.errno not in [errno.EWOULDBLOCK, errno.EAGAIN]:
                    raise
                continue

