#!/usr/bin/env python3
"""M38E guarded driver launcher (steers 3f422ad + 0821351).

chdir + setsid, then BLOCK on an inherited pipe barrier before exec:
the child may not reach the scientific driver until the parent has
durably recorded its PID/PGID (nonce-bound ``launching`` state) and
released the barrier with a GO byte. If the parent dies first, the
pipe closes without a byte and the child exits WITHOUT exec and
without touching any ledger. An inherited lock descriptor (kept open
through exec) keeps the run-ID flock held by the surviving driver even
if the controller dies afterward.

usage: m38e_launch.py <barrier_fd> <lock_fd> <exec_dir> <python>
                      <driver_rel> [args...]
"""
import os
import sys


def main() -> None:
    if len(sys.argv) < 6:
        raise SystemExit("usage: m38e_launch.py <barrier_fd> <lock_fd> "
                         "<exec_dir> <python> <driver_rel> [args...]")
    barrier_fd = int(sys.argv[1])
    lock_fd = int(sys.argv[2])
    exec_dir, python, driver = sys.argv[3:6]
    args = sys.argv[6:]

    os.chdir(exec_dir)
    os.setsid()
    # FD audit (steer e2d5b5e item 3): beyond std streams, only the
    # barrier and the run-lock descriptor may be open. Anything else is
    # a leaked controller descriptor -> exit without exec.
    allowed = {0, 1, 2, barrier_fd, lock_fd}
    for entry in os.listdir("/proc/self/fd"):
        fd = int(entry)
        try:
            if os.readlink(f"/proc/self/fd/{entry}").startswith(
                    "/proc/self/fd"):
                continue                    # the listdir fd itself
        except OSError:
            continue
        if fd not in allowed:
            os.write(2, b"[m38e-launch] unexpected descriptor: abort\n")
            raise SystemExit(4)
    # Barrier: exactly one GO byte authorizes exec. EOF (parent death
    # before durable registration) means exit without exec.
    go = os.read(barrier_fd, 1)
    os.close(barrier_fd)                    # closed before exec
    if go != b"G":
        raise SystemExit(0)                # no exec, no ledger contact
    os.set_inheritable(lock_fd, True)      # driver keeps the flock held
    os.execv(python, [python, driver, *args])


if __name__ == "__main__":
    main()
