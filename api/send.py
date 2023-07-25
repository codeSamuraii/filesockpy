import os
import tqdm
import socket
import pathlib


SEPARATOR = "<SEPARATOR>"


def send_file(file_path, host, port, buff_size, jobs):
    filename = file_path.name
    filesize = file_path.stat().st_size

    s = socket.socket()
    s.connect((host, int(port)))
    # s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with file_path.open('rb') as f:
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