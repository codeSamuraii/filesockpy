import eventlet
import socket
import logging
import pathlib
import io

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FileQueue:
    def __init__(self, file_path: pathlib.Path, buff_size: int = 1024, n_jobs: int = 4):
        self.input = file_path
        self.n_jobs = n_jobs
        self.buff_size = buff_size
        self.pool = eventlet.GreenPool()
        self.queue = eventlet.Queue()

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
            jobs = {
                self.pool.spawn(self._read_and_queue, input_io, self.queue, self.buff_size) for _ in range(self.n_jobs)
            }
            self.pool.waitall()
        finally:
            input_io.close()
    
    @staticmethod
    def _read_and_send(input_io: io.FileIO, output_socket: socket.socket, buff_size: int):
        while True:
            bytes_read = input_io.read(buff_size)
            if not bytes_read:
                break
            else:
                output_socket.sendall(bytes_read)
                logging.debug(f"sent {len(bytes_read)} bytes")

            eventlet.sleep()
    
    def read_and_send(self, output_socket: socket.socket):
        input_io = self.input.open('rb', buffering=self.buff_size)
        try:
            jobs = {
                self.pool.spawn(self._read_and_send, input_io, output_socket, self.buff_size) for _ in range(self.n_jobs)
            }
            self.pool.waitall()
        finally:
            input_io.close()



class FileSend(FileQueue):
    def __init__(self, file_path: pathlib.Path, host: str, port: int, buff_size: int = 1024, n_jobs: int = 2):
        super().__init__(file_path, buff_size, n_jobs)

    @staticmethod
    def _send_queue(queue: eventlet.Queue, s: socket.socket):
        FileSend._read_queue(queue, s.sendall)


if __name__ == '__main__':
    eventlet.monkey_patch()
    logging.basicConfig(level=logging.DEBUG)

    input_path = pathlib.Path('data.bin').resolve()
    n_jobs = 4
    if not eventlet.patcher.is_monkey_patched(socket):
        exit()
    s = socket.socket()
    s.connect(('127.0.0.1', 9898))

    fq = FileQueue(input_path, n_jobs=n_jobs)
    fq.read_and_send(s)
    fq.pool.waitall()
