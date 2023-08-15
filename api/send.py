import time
import tqdm
import socket
import pathlib

from api.io import FileQueue
from api.misc import create_progressbar


def send_file(file_path, host, port, buff_size, jobs):
    s = socket.socket()
    s.connect((host, int(port)))
    send_header(file_path, buff_size, jobs, s)

    progress = create_progressbar(file_path.stat().st_size, file_path.name)
    fq = FileQueue(file_path, n_jobs=jobs, buff_size=buff_size)
    fq.read_and_send(s, progress)
    progress.close()
    
    s.close()

    return fq.duration


def send_header(file_path, buff_size, jobs, socket):
    header = f"{file_path.stat().st_size}||{buff_size}||{jobs}"
    socket.sendall(header.encode('utf-8'))