# filesockpy

Multi-threaded file transfer.

![filesockpy_demo](https://github.com/codeSamuraii/filesockpy/assets/17270548/c56a3f62-ce60-426d-be34-43632d948057)

```
usage: filesockpy [-h] (-i INPUT | -o OUTPUT) [--jobs JOBS] [--buff_size BUFF_SIZE] [--verbose] host

Transfer files via sockets in Python.

Examples:
> Send a file locally to port 9696:		python filesockpy -i file.bin 127.0.0.1:9696
> Receive from anyone and store in tmp:		python filesockpy -o /tmp/test.bin 0.0.0.0:<port>
> Custom buffer size and number of jobs:	python filesockpy --jobs 8 --buff_size 1024 -i ...

positional arguments:
  host                  host to connect/bind to [<ip>:<port>]

options:
  -h, --help            show this help message and exit
  --jobs JOBS, -j JOBS  Number of jobs to run in parallel. Default: 4
  --buff_size BUFF_SIZE, -bs BUFF_SIZE
                        Size of the reading buffer to use. Default: 4096
  --verbose, -v         Activate verbose logging.

I/O:
  path to input OR output file

  -i INPUT, --input INPUT
                        path to input file to transfer
  -o OUTPUT, --output OUTPUT
                        path to output file to receive
```
