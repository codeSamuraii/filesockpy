import tqdm
import socket
import logging
from datetime import datetime

from api.io import FileQueue

log = logging.getLogger(__name__)


def receive_file(file_path, port, buff_size, jobs, progress_callback):
    s = socket.socket()
    s.bind(('0.0.0.0', int(port)))
    s.listen(1)
    conn, addr = s.accept()

    start = datetime.now()
    fq = FileQueue(file_path, n_jobs=jobs, buff_size=buff_size)
    fq.receive_and_callback(conn, callback=lambda b: progress_callback(len(b)))
    fq.pool.waitall()
    stop = datetime.now()

    conn.close()
    s.close()

    return (stop - start).microseconds / 1000