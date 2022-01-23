import socket
import errno


class Socket:
    def __init__(self, addr, conf, bound=False, family=socket.AF_INET, sock_type=socket.SOCK_STREAM) -> None:
        sock = socket.socket(family, sock_type)
        self.sock = self.add_options(sock)
        self.cfg = conf

        if not bound:
            self.bind(addr)

    def add_options(self, sock, **kwargs):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise
        sock.setblocking(False)
        if not sock.get_inheritable():
            sock.set_inheritable(True)
        return sock
    
    def bind(self, addr):
        self.sock.bind(addr)
    
    def listen(self):
        self.sock.listen(self.cfg.queue)
    
    def ensure_closed(self):
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError as e:
                self.cfg.log.info('Error closing empty socket\n{}'.format(e))
            self.sock = None
