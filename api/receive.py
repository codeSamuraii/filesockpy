import time
import tqdm
import socket
import logging
from datetime import timedelta

from api.io import FileQueue
from api.misc import get_duration, sizeof_fmt, create_progressbar, close_progressbar

log = logging.getLogger(__name__)


def start_listening(port):
    sock = socket.socket()
    address = ('0.0.0.0', int(port))
    sock.bind(address)
    log.debug(f'Binding to {address}.')

    sock.listen(0)
    log.info(f'Listening on port {port}.')

    conn, peer_addr = sock.accept()
    log.info(f'Connection from {peer_addr}.')

    return conn

def receive_header(socket):
    header = socket.recv(2048).decode('utf-8')
    file_size, buff_size, jobs = header.split('||')
    log.info(f'Incoming file: {sizeof_fmt(int(file_size))}')
    log.debug(f'({jobs} jobs - buffer: {buff_size} bytes)')

    return int(file_size), int(buff_size), int(jobs)


def receive_file(file_path, port):
    with start_listening(port) as conn:
        file_size, buff_size, jobs = receive_header(conn)
        progress = create_progressbar(file_size, file_path.name)
        fq = FileQueue(file_path, n_jobs=jobs, buff_size=buff_size)
        fq.receive_and_save(conn, progress_callback=progress)
        progress.close()

    return file_size, fq.duration
