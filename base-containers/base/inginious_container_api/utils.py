# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import tempfile
import subprocess
import resource
import stat
import time

def set_limits():  # TODO: check if run as root or not
    os.setgid(4242)
    os.setuid(4242)
    resource.setrlimit(resource.RLIMIT_NPROC, (1000, 1000))


def set_executable(filename):
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)


def execute_process(args, stdin_string="", internal_command=False):
    if not isinstance(args, list):
        args = [args]

    stdin = tempfile.TemporaryFile()
    stdin.write(stdin_string.encode('utf-8'))
    stdin.seek(0)

    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    if internal_command:
        pr = subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr)
    else:
        set_executable(args[0])
        pr = subprocess.Popen(args, preexec_fn=set_limits, stdin=stdin, stdout=stdout, stderr=stderr)
    pr.wait()
    stdout.seek(0)
    stderr.seek(0)
    return stdout.read(), stderr.read()

def start_ssh_server():
    # Generate password
    password, _ = execute_process(["/usr/bin/openssl", "rand", "-base64", "10"], internal_command=True)
    password = password.decode('utf8').strip()
    ssh_user = "worker"  # or root with Kata
    execute_process(["/usr/bin/bash", "-c", "echo '{}:{}' | chpasswd".format(ssh_user, password)],
                    internal_command=True)
    # generate the host keys
    execute_process(["/usr/bin/ssh-keygen", "-A"], internal_command=True)

    # remove /run/nologin if it exists
    if os.path.exists("/run/nologin"):
        os.unlink("/run/nologin")

    # Start the ssh server
    execute_process(["/usr/sbin/sshd",
                    "-p", "22",
                    "-o", "PermitRootLogin=no",
                    "-o", "PasswordAuthentication=yes", "-o", "StrictModes=no", "-o",
                    "AllowUsers={}".format(ssh_user)], internal_command=True)
    return ssh_user, password


def ssh_wait(ssh_user):
    # Wait until someone connects to the server. Returns 0 if it went well
    connected_workers = 0
    attempts = 0
    while connected_workers == 0 and attempts < 120:  # wait max 2min
        time.sleep(1)
        stdout, stderr = execute_process(
            ["/bin/bash", "-c", "ps -f -C sshd | grep '{}@pts' | wc -l".format(ssh_user)], internal_command=True)
        connected_workers = int(stdout)
        attempts += 1

    # If someone is connected, wait until no one remains
    if connected_workers != 0:
        while connected_workers != 0:
            time.sleep(1)
            stdout, stderr = execute_process(
                ["/bin/bash", "-c", "ps -f -C sshd | grep '{}@pts' | wc -l".format(ssh_user)], internal_command=True)
            connected_workers = int(stdout)
        return 0
    else:
        print("NO ONE CONNECTED")
        return 1
