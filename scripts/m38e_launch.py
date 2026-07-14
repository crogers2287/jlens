#!/usr/bin/env python3
"""M38E guarded driver launcher (steers 3f422ad + 0821351 + 4cb5caa).

Two-way handshake: after chdir + setsid + a strict FD audit, the child
writes exactly one READY record (self-observed pid/pgid/sid/cwd and
/proc/self/exe identity) through a dedicated inherited pipe, then blocks
on the GO pipe. The parent verifies the READY proof, durably registers
ownership, and only then sends GO. EOF/timeout/mismatch or parent death
before GO => the child exits WITHOUT exec and without ledger contact.
Behind the barrier the running interpreter (/proc/self/exe) and the
target executable are re-proven by canonical path, device, inode, mode,
size, and sha256 before exec (steer 4cb5caa item 2).

usage: m38e_launch.py <ready_fd> <go_fd> <lock_fd> <exe_identity_json>
                      <exec_dir> <python> <driver_rel> [args...]
"""
import hashlib
import json
import os
import sys


def file_identity(path):
    real = os.path.realpath(path)
    st = os.stat(real)
    return {"canonical": real, "dev": st.st_dev, "inode": st.st_ino,
            "mode": st.st_mode, "size": st.st_size,
            "sha256": hashlib.sha256(open(real, "rb").read()).hexdigest()}


def main():
    if len(sys.argv) < 8:
        raise SystemExit("usage: m38e_launch.py <ready_fd> <go_fd> "
                         "<lock_fd> <exe_identity_json> <exec_dir> "
                         "<python> <driver_rel> [args...]")
    ready_fd = int(sys.argv[1])
    go_fd = int(sys.argv[2])
    lock_fd = int(sys.argv[3])
    exe_ident = json.loads(sys.argv[4])
    exec_dir, python, driver = sys.argv[5:8]
    args = sys.argv[8:]

    os.chdir(exec_dir)
    os.setsid()

    allowed = {0, 1, 2, ready_fd, go_fd, lock_fd}
    for entry in os.listdir("/proc/self/fd"):
        fd = int(entry)
        try:
            if os.readlink(f"/proc/self/fd/{entry}").startswith(
                    "/proc/self/fd"):
                continue
        except OSError:
            continue
        if fd not in allowed:
            os.write(2, b"[m38e-launch] unexpected descriptor: abort\n")
            raise SystemExit(4)

    pid = os.getpid()
    ready = {"pid": pid, "pgid": os.getpgid(pid), "sid": os.getsid(pid),
             "cwd": os.getcwd(),
             "self_exe": file_identity("/proc/self/exe")}
    os.write(ready_fd, (json.dumps(ready) + "\n").encode())
    os.close(ready_fd)

    go = os.read(go_fd, 1)
    os.close(go_fd)
    if go != b"G":
        raise SystemExit(0)

    running = file_identity("/proc/self/exe")
    target = file_identity(python)
    for got in (running, target):
        for k in ("canonical", "dev", "inode", "mode", "size", "sha256"):
            if got[k] != exe_ident.get(k):
                os.write(2, b"[m38e-launch] executable identity changed: "
                            b"abort\n")
                raise SystemExit(5)
    os.set_inheritable(lock_fd, True)
    os.execv(target["canonical"], [target["canonical"], driver, *args])


if __name__ == "__main__":
    main()
