import os
import signal
import errno
import select


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
                read = select.select([self.sock], [], [], 1.1)
                if not read or (read and self.sock not in read[0]):
                    continue
                conn, addr = self.sock.accept()
            except OSError as e:
                if e.errno not in [errno.EWOULDBLOCK, errno.EAGAIN]:
                    raise
                continue

            try:
                req = conn.recv(1024)
                self.log.info('We got: {}'.format(req))
            except OSError:
                pass
            
            # Dummy Response Header + Message
            self.log.debug('Accepted connection: {} from {}'.format(addr, self.worker_id))
            data = b'HTTPP/1.1 200 OK\r\n'
            n = conn.send(data)
            conn.send(b'Content-Type: text/html\r\n')#Content-Type: text/html\r\n\r\n<b>Hello World</b>')
            conn.send(b'Allow: GET, POST, PUT\r\n')
            conn.send(b'Server: Servey/0.0.1\r\n\r\n')
            conn.send(b'Hello World')
            conn.close()
            self.log.debug('Message sent')
