import os
import signal
from sock import Socket
from signals import sigs

class MasterP:
    WORKERS = {}
    def __init__(self, config) -> None:
        self.cfg = config
        self.log = self.cfg.log
    
    def sigint_handler(self, sig_num, frame):
        master_id = os.getpid()
        self.log.info('[{}] Master: Closing connection'.format(master_id))
        self.log.info('[{}] Shutting down workers'.format(os.getpid()))
        os._exit(1)

    def sigint_c_handler(self, sig_num, frame):
        self.log.info('[{}] is shutting down'.format(os.getpid()))
        os._exit(1)
    
    def sigchild_handler(self, sig_num, frame):
        pid = self.wait()
        if pid >= 0:
            pass

    def init_signals(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGCHLD, self.sigchild_handler)

    def kill_workers(self):
        for pid, worker in self.WORKERS.items():
            worker.kill()

    def wait(self):
        try:
            pid, status = os.waitpid(-1, os.WUNTRACED | os.WCONTINUED)
        except OSError as e:
            self.log.debug('Unable to wait on child: {}'.format(e))
            return -1

        if os.WIFEXITED(status):
            self.log.debug('[{}] exited with status {}\n'.format(pid, os.WEXITSTATUS(status)))
            self.WORKERS.pop(pid, None)
        elif os.WIFSTOPPED(status):
            self.log.debug('[{}] received stop signal {}\n'.format(pid, os.WSTOPSIG(status)))
        elif os.WIFCONTINUED(status):
            self.log.debug('[{}] received stop signal {}\n'.format(pid, os.WSTOPSIG(status)))
        elif os.WIFSIGNALED(status):
            self.log.debug('[{}] received {} signal\n'.format(pid, sigs[os.WTERMSIG(status)]))
            self.WORKERS.pop(pid, None)
        else:
            pass
        return pid
    
    def start(self):
        sock = Socket(self.cfg.addr, self.cfg)
        self.init_signals()
        for _ in range(self.cfg.num_worker):
            pid = os.fork()
            if pid == -1:
                self.log.error('Fork Error!')
                return
            if pid != 0:
                continue
            signal.signal(signal.SIGINT, self.sigint_c_handler)
            sock.sock.listen()
            while True:
                p_id = os.getpid()

                self.log.info('Waiting for connection...')

                try:
                    conn, addr = sock.sock.accept()
                except BlockingIOError:
                    continue
                
                self.log.info('Accepted connection: {} from {}'.format(addr, p_id))

                n = conn.send(b'\r\nContent-Type: text/plain; Hello World')
                if n != len('\r\nContent-Type: text/plain; Hello World'):
                    self.log.info('Unable to send data')
                    raise Exception('Something bad has happened')
                self.log.info('Message sent')
                # req = conn.recv(1024)
                # self.log.debug('[{}] Found: {}'.format(p_id, req))
    
    # def ensure_workers(self):
        # for 
    
    def run(self):
        self.start()
        while True:
            pass
    
    def start_worker(self):
        pass


if __name__ == '__main__':
    from config import Config
    config = Config('127.0.0.1:8000', nworker=3)
    serv = MasterP(config)
    serv.run()
