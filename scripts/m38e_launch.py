#!/usr/bin/env python3
"""Minimal M38E driver launcher (steer 3f422ad): chdir + setsid + exec.

Because setsid() is called in THIS process and exec replaces its image,
the launcher's PID is the driver's PID and the owned process-group ID —
one exact identity, never rediscovered by name.

usage: m38e_launch.py <exec_dir> <python> <driver_rel> [args...]
"""
import os
import sys


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit("usage: m38e_launch.py <exec_dir> <python> "
                         "<driver_rel> [args...]")
    exec_dir, python, driver = sys.argv[1:4]
    args = sys.argv[4:]
    os.chdir(exec_dir)
    os.setsid()
    os.execv(python, [python, driver, *args])


if __name__ == "__main__":
    main()
