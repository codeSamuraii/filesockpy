import os
import tqdm
import socket
import pathlib


SEPARATOR = "<SEPARATOR>"


def send_file(file_path, host, buff_size, jobs):
    file = pathlib.Path(file_path).resolve()
    filename = file.name
    filesize = file.stat().st_size

    s = socket.socket()
    ip, port = host.split(':')
    s.connect((ip, int(port)))
    # s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with file.open('rb') as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(buff_size)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    # close the socket
    s.close()