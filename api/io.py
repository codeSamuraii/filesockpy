import eventlet
import socket
import logging
import pathlib
import time
import io
from datetime import datetime

from api.misc import eventlet_routine, get_duration

log = logging.getLogger(__name__)


class FileQueue:
    def __init__(self, file_path: pathlib.Path, n_jobs: int = 4, buff_size: int = 1024):
        eventlet_routine()
        self.input = file_path
        self.n_jobs = n_jobs
        self.buff_size = buff_size
        self.pool = eventlet.GreenPool()
        self.queue = eventlet.Queue()
        self._t_start = None
        self._t_stop = None

    @property
    def duration(self):
        if self._t_start is not None:
            return get_duration(self._t_start, self._t_stop)
    
    def _start_t(self):
        self._t_start = time.monotonic()
    
    def _stop_t(self):
        self._t_stop = time.monotonic()
        log.debug(f'FQ duration: {self.duration}')

    @staticmethod
    def _read_and_queue(input_io: io.FileIO, output_queue: eventlet.Queue, buff_size: int):
        while True:
            bytes_read = input_io.read(buff_size)
            if not bytes_read:
                break
            else:
                output_queue.put_nowait(bytes_read)

            eventlet.sleep()
    
    def read_and_queue(self):
        input_io = self.input.open('rb', buffering=self.buff_size)
        try:
            for _ in range(self.n_jobs):
                self.pool.spawn_n(self._read_and_queue, input_io, self.queue, self.buff_size)

            self.pool.waitall()
        finally:
            input_io.close()
    
    @staticmethod
    def _read_and_send(input_io: io.FileIO, output_socket: socket.socket, buff_size: int, progress_callback: callable = None):
        while True:
            bytes_read = input_io.read(buff_size)
            if not bytes_read:
                break
            else:
                output_socket.sendall(bytes_read)
                if progress_callback:
                    progress_callback(len(bytes_read))

            eventlet.sleep()
    
    def read_and_send(self, output_socket: socket.socket, progress_callback: callable = None):
        self._start_t()
        input_io = self.input.open('rb', buffering=self.buff_size)
        try:
            for _ in range(self.n_jobs):
                self.pool.spawn_n(self._read_and_send, input_io, output_socket, self.buff_size, progress_callback)

            self.pool.waitall()
        finally:
            input_io.close()
        self._stop_t()
    
    @staticmethod
    def _unqueue_and_callback(input_queue: eventlet.Queue, callback: callable):
        while True:
            item = input_queue.get_nowait()
            if not item:
                break
            else:
                callback(item)
            
            eventlet.sleep()
    
    def unqueue_and_callback(self, callback: callable):
        for _ in range(self.n_jobs):
            self.pool.spawn_n(self._enqueue_and_callback, self.queue, callback)

        self.pool.waitall()
    
    @staticmethod
    def _receive_and_callback(input_socket: socket.socket, callback: callable, buff_size: int, progress_callback: callable):
        while True:
            bytes_read = input_socket.recv(buff_size)
            if not bytes_read:
                break
            else:
                callback(bytes_read)
                if progress_callback:
                    progress_callback(len(bytes_read))
            
            eventlet.sleep()
    
    def receive_and_callback(self, input_socket: socket.socket, callback: callable, progress_callback: callable = None):
        for _ in range(self.n_jobs):
            self.pool.spawn_n(self._receive_and_callback, input_socket, callback, self.buff_size, progress_callback)

        self.pool.waitall()
    
    def receive_and_log(self, input_socket: socket.socket):
        self.receive_and_callback(input_socket, lambda x: log.debug(f"received {len(x)} bytes"))

    def receive_and_save(self, input_socket: socket.socket, progress_callback: callable = None):
        self._start_t()
        output_io = self.input.open('wb', buffering=0)
        try:
            self.receive_and_callback(input_socket, output_io.write, progress_callback)
        finally:
            output_io.close()
        self._stop_t()