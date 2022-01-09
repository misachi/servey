import logging
import ipaddress
from multiprocessing import cpu_count

from errors import ConfigError


logger = logging.getLogger(__name__)
CPU_COUNT = cpu_count()
MEM_SIZE = 100 * 1024 * 1024


class Config:
    def __init__(self, addr, ncpus=None, nworker=None, mem_sz=None):
        self.addr = addr
        self.num_cpu = ncpus

        if mem_sz is None:
            self.mem_limit = MEM_SIZE
        self.num_worker = nworker
    
    @property
    def addr(self):
        return self._addr
    
    @addr.setter
    def addr(self, ip_addr):
        try:
            ipaddress.ip_address(ip_addr)
        except ValueError as e:
            logger.exception('Config addr: Invalid IP address: {}'.format(ip_addr))
            raise ConfigError('Config addr: Invalid IP address')
        
        self._addr = ip_addr
    
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
        return self.mem_limit

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