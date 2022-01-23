import os
import time
import sys
import signal
from sock import Socket
from signals import sigs

from worker import Worker


class MasterP:
    WORKERS = {}
    def __init__(self, config) -> None:
        self.cfg = config
        self.log = self.cfg.log
        self.master_id = os.getpid()
        self.sock = None
    
    def sigint_handler(self, sig_num, frame):
        self.log.info('[{}] Master: Closing connection'.format(self.master_id))
        # self.kill_workers()
        time.sleep(0.2)
        os._exit(0)

    def sigchild_handler(self, sig_num, frame):
        try:
            pid, status = os.waitpid(-1, os.WUNTRACED | os.WCONTINUED)
        except OSError as e:
            self.log.debug('Unable to wait on child: {}'.format(e))
            return -1

        if pid in self.WORKERS:
            if os.WIFEXITED(status):
                self.log.debug('[{}] exited with status {}\n'.format(pid, os.WEXITSTATUS(status)))
                self.WORKERS.pop(pid, None)
            elif os.WIFSTOPPED(status):
                self.log.debug('[{}] received stop signal {}\n'.format(pid, os.WSTOPSIG(status)))
            elif os.WIFCONTINUED(status):
                self.log.debug('[{}] received continue signal {}\n'.format(pid, os.WSTOPSIG(status)))
            elif os.WIFSIGNALED(status):
                self.log.debug('[{}] received {} signal\n'.format(pid, sigs[os.WTERMSIG(status)]))
                self.WORKERS.pop(pid, None)

    def init_signals(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGCHLD, self.sigchild_handler)

    def kill_workers(self):
        for pid, _ in self.WORKERS.items():
            os.kill(pid, signal.SIGTERM)

    def new_children(self, num_workers):
        self.sock = Socket(self.cfg.addr, self.cfg)

        for _ in range(num_workers):
            worker = Worker(self.sock, os.getpid(), self.cfg)
            pid = os.fork()
            if pid == -1:
                self.log.error('Fork Error!')
                return

            if pid != 0:
                self.WORKERS[pid] = worker
                continue
            
            worker.run()


    def start(self):
        self.init_signals()
        sys.stdout.write('[{}] Master is starting\n'.format(self.master_id))
        sys.stdout.write('starting worker processes\n')
        sys.stdout.flush()

        try:
            self.new_children(self.cfg.num_worker)
        except Exception:
            pass

        if self.master_id == os.getpid():
            self.sock.ensure_closed()
    
    def ensure_workers(self):
        num_workers = len(self.WORKERS)

        if num_workers < self.cfg.num_worker:
            self.new_children(self.cfg.num_worker - num_workers)
        elif num_workers > self.cfg.num_worker:
            if self.WORKERS:
                worker_pids = list(self.WORKERS.keys())
                for _ in range(num_workers - self.cfg.num_worker):
                    pid = worker_pids.pop()
                    os.kill(pid, signal.SIGTERM)
                    self.WORKERS.pop(pid, None)

    def run(self):
        self.start()
        self.ensure_workers()
        while True:
            time.sleep(0.5)
