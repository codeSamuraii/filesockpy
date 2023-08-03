import tqdm
import socket
import pathlib
from datetime import datetime

from api.io import FileQueue


def send_file(file_path, host, port, buff_size, jobs, progress_callback=None):
    s = socket.socket()
    s.connect((host, int(port)))

    start = datetime.now()
    fq = FileQueue(file_path, n_jobs=jobs, buff_size=buff_size)
    fq.read_and_send(s, progress_callback)
    fq.pool.waitall()
    stop = datetime.now()

    s.close()
    return (stop - start).microseconds / 1000