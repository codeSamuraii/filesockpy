import pathlib
import argparse

from api import send, receive


def get_cli_args():
    parser = argparse.ArgumentParser(
        prog='filesockpu',
        formatter_class=argparse.RawTextHelpFormatter,
        description='''Transfer files via sockets in Python.\n
                    \r[...]
                    \r[...]
                    \r[...]''', \
    )
    parser.add_argument('host', type=str, help='host to connect/bind to')
    io = parser.add_argument_group('I/O', 'path to input OR output file')
    file = io.add_mutually_exclusive_group(required=True)
    file.add_argument('-i', '--input', type=str, help='path to input file to transfer')
    file.add_argument('-o', '--output', type=str, help='path to output file to receive')
    parser.add_argument('--jobs', '-j', type=int, default=2, help="Number of jobs to run in parallel")
    parser.add_argument('--buff_size', '-bs', type=int, default=256, help="Size of the reading buffer to use. Default: 256")
    return parser.parse_args()


def main():
    arguments = get_cli_args()
    jobs = arguments.jobs
    buff_size = arguments.buff_size
    host_ip, host_port = arguments.host.split(':')

    if arguments.input:
        print(f'> Input file: {arguments.input}')
        input_path = pathlib.Path(arguments.input).resolve()
        send.send_file(input_path, host_ip, host_port, buff_size, jobs)

    if arguments.output:
        print(f'> Output file: {arguments.output}')
        print('Doing nothing...')


if __name__ == '__main__':
    main()