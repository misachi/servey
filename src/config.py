import ipaddress
from multiprocessing import cpu_count
from log.logging import logger

from errors import ConfigError


CPU_COUNT = cpu_count()
MEM_SIZE = 100 * 1024 * 1024


class Config:
    def __init__(self, addr, ncpus=None, nworker=None, mem_sz=None):
        self.addr = addr
        self.num_cpu = ncpus
        self.mem_limit = mem_sz
        self.num_worker = nworker
    
    @property
    def addr(self):
        _addr, port = self._addr.split(':')
        return _addr, int(port)
    
    @addr.setter
    def addr(self, addr):
        try:
            ip_addr = addr.split(':')[0]
            ipaddress.ip_address(ip_addr)
        except ValueError as e:
            logger.exception('Config addr: Invalid IP address({}): {}'.format(ip_addr, e))
            raise ConfigError('Config addr: Invalid IP address')
        
        self._addr = addr
    
    @property
    def num_cpu(self):
        return self._num_cpu
    
    @num_cpu.setter
    def num_cpu(self, cnt):
        if cnt is None:
            cnt = 1

        if cnt > CPU_COUNT:
            logger.warning(
                'Config num_cpu: Set cpu limit({}) exceeds total cpus in the system({})'.format(cnt, CPU_COUNT))
        
        try:
            int(cnt)
        except ValueError as e:
            raise ConfigError('Config num_cpu: {}'.format(e))
        
        self._num_cpu = cnt

    @property
    def mem_limit(self):
        return self._mem_limit
    
    @mem_limit.setter
    def mem_limit(self, mem_sz):
        if mem_sz is None:
            self._mem_limit = MEM_SIZE
        else:
            self._mem_limit = mem_sz

    @property
    def num_worker(self):
        return self._num_worker
    
    @num_worker.setter
    def num_worker(self, worker_cnt):
        if worker_cnt is None:
            worker_cnt = 2

        if worker_cnt > (CPU_COUNT*2):
            logger.warning(
                'Config num_worker: Setting a very high number \
                of worker processes({}) can affect performance'.format(worker_cnt))
        
        self._num_worker = worker_cnt
    
    @property
    def log(self):
        return logger
