# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import tempfile
import subprocess
import resource
import stat

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
