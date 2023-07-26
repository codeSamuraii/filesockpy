import eventlet
eventlet.monkey_patch()
import socket
import logging
import pathlib
import io

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FileQueue:
    def __init__(self, file_path: pathlib.Path, buff_size: int = 1024, n_jobs: int = 2):
        self.input = file_path
        self.n_jobs = n_jobs
        self.buff_size = buff_size
        self.pool = eventlet.GreenPool(n_jobs + 1)
        self.read_pile = eventlet.GreenPile(self.pool)
        self.write_pile = eventlet.GreenPile(self.pool)
        self.queue = eventlet.Queue()

    def read_file_to_queue(self, alt_input_io: io.FileIO = None):
        input_io = alt_input_io or self.input.open('rb', buffering=0)
        try:
            self._file_to_queue(input_io, self.queue, self.buff_size, self.n_jobs)
        finally:
            input_io.close()

    @staticmethod
    def _file_to_queue(input_io: io.FileIO, queue: eventlet.Queue, buff_size: int, n_jobs: int):
        while True:
            bytes_read = input_io.read(buff_size * n_jobs)
    
            if not bytes_read:
                queue.put_nowait('\0')
                log.debug("> sending EOF")
                break

            log.debug(f'> {len(bytes_read)} bytes read from file')
            chunks = (bytes_read[i:i+buff_size] for i in range(0, len(bytes_read), buff_size))
            for chunk in chunks:
                queue.put_nowait(chunk)

            eventlet.sleep()
    
    @classmethod
    def read(cls, file_path: pathlib.Path, buff_size: int = 1024, n_jobs: int = 2):
        file_queue = cls(file_path, buff_size, n_jobs)
        file_queue.read_pile.spawn(file_queue.read_file_to_queue)
        return file_queue

    @staticmethod
    def _read_queue(queue: eventlet.Queue, callback: callable):
        try:
            while queue_item := queue.get(timeout=5.0):
                if queue_item == '\0':
                    log.debug('< end of queue')
                    queue.put_nowait('\0')
                    break

                log.debug(f'< {len(queue_item)} bytes received')
                callback(queue_item)
                eventlet.sleep()
    
        except eventlet.queue.Empty:
            log.warn('< queue empty for 5 seconds !')

        eventlet.sleep()
    
    @staticmethod
    def _log_queue(queue: eventlet.Queue):
        FileQueue._read_queue(queue, log.info)

    # def queue_to_file(self):
    #     while queue_item := self.queue.get():
    #         print(queue_item)   
 
    # def write(cls, file_path: pathlib.Path, buff_size: int = 256, n_jobs: int = 2):
    #     object = cls(file_path, buff_size, n_jobs)
    #     object.pool.spawn(object.queue_to_file)
    #     return object, object.queue

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

    fq = FileQueue.read(input_path, buff_size=32, n_jobs=n_jobs)
    writers = [fq.write_pile.spawn(FileSend._send_queue, fq.queue, s) for _ in range(n_jobs)]
    fq.pool.waitall()
