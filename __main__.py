import pathlib
import argparse
import logging

from api import misc, send, receive


log = logging.getLogger("filesockpy")



def get_cli_args():
    parser = argparse.ArgumentParser(
        prog='filesockpy',
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
    parser.add_argument('--jobs', '-j', type=int, default=4, help="Number of jobs to run in parallel. Default: 4")
    parser.add_argument('--buff_size', '-bs', type=int, default=4096, help="Size of the reading buffer to use. Default: 4096")
    parser.add_argument('--verbose', '-v', action='store_true', help="Activate verbose logging.")
    return parser.parse_args()


def main():
    misc.eventlet_routine()

    arguments = get_cli_args()
    jobs = arguments.jobs
    buff_size = arguments.buff_size
    host_ip, host_port = arguments.host.split(':')

    if arguments.verbose:
        logging.basicConfig(level=logging.DEBUG)
        log.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        log.setLevel(logging.INFO)

    if arguments.input:
        input_path = pathlib.Path(arguments.input).resolve()
        size, s_size = input_path.stat().st_size, misc.sizeof_fmt(input_path.stat().st_size)
        print(f'> Input file: {input_path}\n- Size: {s_size}\n- Jobs: {jobs}\n- Buffer size: {buff_size}')
        duration = send.send_file(input_path, host_ip, host_port, buff_size, jobs)
        rate = misc.compute_rate(size, duration)
        print(f'> Duration: {duration} — Rate: {rate:.2f} MiB/s')

    if arguments.output:
        output_path = pathlib.Path(arguments.output).resolve()
        print(f'> Output file: {output_path}')
        size, duration = receive.receive_file(output_path, host_port)
        rate = misc.compute_rate(size, duration)
        print(f'> Duration: {duration} — Rate: {rate:.2f} MiB/s')

if __name__ == '__main__':
    main()