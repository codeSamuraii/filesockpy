import time
import tqdm
import socket
import logging
import eventlet
from datetime import timedelta
from functools import partial
from eventlet import debug as eventlet_debug

log = logging.getLogger(__name__)


ONE_KiB = 1024
ONE_MiB = 1024 * ONE_KiB

def compute_rate(size_in_bytes, duration):
    """Return the transfer rate in MiB/s."""
    return (size_in_bytes / ONE_MiB) / duration.total_seconds()


def get_duration(start, stop=None):
    """Return the duration in milliseconds between two timestamps."""
    if stop is None:
        stop = time.monotonic()
    return timedelta(seconds=(stop - start))


def eventlet_routine():
    """Patch imports and disable multiple readers warnings."""
    log.debug("> Entering eventlet routine.")

    if not eventlet.patcher.is_monkey_patched(socket):
        log.info("- Patching imports...")
        eventlet.monkey_patch()

        log.debug("- Disabling multiple readers warnings.")
        eventlet_debug.hub_prevent_multiple_readers(False)
    else:
        log.debug("* Eventlet already patched.")


def do_nothing(*args, **kwargs):
    """Takes any arguments and does nothing."""
    pass


def create_progressbar(file_size, file_name=None, verbosity=False):
    """Create a progressbar if verbosity is set and return its update callback."""

    def update_progress(pgbr, value=None):
        if value is None:
            pgbr.close()
        else:
            pgbr.update(value)
    
    if not verbosity:
        pgbr = tqdm.tqdm(range(file_size), f"* {file_name or '(File)'}", unit="B", unit_scale=True, unit_divisor=1024)
        pgbr.clear()
        update_progress_partial = partial(update_progress, pgbr)
        update_progress_partial.close = pgbr.close
        return update_progress_partial
    else:
        return do_nothing


def close_progressbar(progress_callback):
    progress_callback(None)


# By Fred Cirera - https://stackoverflow.com/a/1094933
def sizeof_fmt(nbytes, suffix="B"):
    """Return a human readable file size from a number of bytes."""
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(nbytes) < 1024.0:
            return f"{nbytes:3.1f}{unit}{suffix}"
        nbytes /= 1024.0
    return f"{nbytes:.1f}Yi{suffix}"

