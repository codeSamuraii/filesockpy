import pathlib
import eventlet


class FileQueue:
    def __init__(self, file_path: pathlib.Path, buff_size: int = 1024, n_jobs: int = 2):
        self.input = file_path
        self.n_jobs = n_jobs
        self.buff_size = buff_size
        self.pool = eventlet.GreenPool(n_jobs + 1)
        self.queue = eventlet.Queue()

    def read_file_to_queue(self):
        f = self.input.open('rb')
        while True:
            bytes_read = f.read(self.buff_size)
            if not bytes_read:
                self.queue.put_nowait('\0')
                break
            self.queue.put_nowait(bytes_read)
            print(f'> {len(bytes_read)} bytes read')
            eventlet.sleep()
        f.close()
    
    @classmethod
    def read(cls, file_path: pathlib.Path, buff_size: int = 1024, n_jobs: int = 2):
        object = cls(file_path, buff_size, n_jobs)
        object.pool.spawn_n(object.read_file_to_queue)
        return object, object.queue

    @staticmethod
    def _print_queue(queue):
        flag = False
        while not flag:
            try:
                queue_item = queue.get_nowait()
                if queue_item == '\0':
                    print('\n\nFin de queue\n\n')
                    flag = True
                else:
                    print(f'< {len(queue_item)} bytes read')
            except eventlet.queue.Empty:
                if flag:
                    break
            eventlet.sleep()

    # def queue_to_file(self):
    #     while queue_item := self.queue.get():
    #         print(queue_item)   
 
    # def write(cls, file_path: pathlib.Path, buff_size: int = 256, n_jobs: int = 2):
    #     object = cls(file_path, buff_size, n_jobs)
    #     object.pool.spawn(object.queue_to_file)
    #     return object, object.queue


if __name__ == '__main__':
    input_path = pathlib.Path('/tmp/input.pdf').resolve()
    fq, q = FileQueue.read(input_path)
    FileQueue._print_queue(q)
    # fq.pool.spawn_n(_print_queue, fq.queue)
    fq.pool.waitall()