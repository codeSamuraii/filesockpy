import tqdm
import socket
import logging
import eventlet
from eventlet import debug as eventlet_debug

log = logging.getLogger(__name__)


def eventlet_routine():
    log.debug("> Entering eventlet routine.")

    if not eventlet.patcher.is_monkey_patched(socket):
        log.info("- Patching imports...")
        eventlet.monkey_patch()

        log.debug("- Disabling multiple readers warnings.")
        eventlet_debug.hub_prevent_multiple_readers(False)
    else:
        log.debug("* Eventlet already patched.")


def create_progressbar(verbosity, file_path):
    if not verbosity:
        pgbr = tqdm.tqdm(range(file_path.stat().st_size), f"* {file_path.name}", unit="B", unit_scale=True, unit_divisor=1024)
        pgbr.clear()
        return pgbr.close, pgbr.update
    else:
        return do_nothing, do_nothing


def do_nothing(*args, **kwargs):
    pass