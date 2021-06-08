# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
import sys
import inginious_container_api.run_student


# Simply runs run_student with no cmd and ssh set to True
def ssh_student(cmd=None, memory=0, hard_time=0, time=0, container=None, share_network=False):
    inginious_container_api.run_student.run_student(cmd=cmd, container=container, time_limit=time,
                hard_time_limit=hard_time, memory_limit=memory,
                share_network=share_network,
                stdin=sys.stdin.fileno(), stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno(),
                signal_handler_callback=inginious_container_api.run_student._hack_signals, ssh=True)