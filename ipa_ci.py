#!/usr/bin/python
# Copyright (c) 2014 Red Hat, Inc. All rights reserved.
#
# This copyrighted material is made available to anyone wishing
# to use, modify, copy, or redistribute it subject to the terms
# and conditions of the GNU General Public License version 2.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

import sys
import os
import paramiko
import util
import subprocess
from common_ci import ExistingNodes
from common_ci import SetupRestraint


def beaker_run():
    workspace = os.environ.get('WORKSPACE')
    if not workspace:
        util.log.error("Failed to find WORKSPACE env variable.")
        sys.exit(1)
    else:
        util.log.info("WORKSPACE env variable is %s." % workspace)
    restraint_dir = ("ipa-tests/restraint")
    restraint_loc = os.path.join(workspace, restraint_dir)

    resources = ExistingNodes()
    resources.env_check()

    my_nodes = resources.node_check()
    util.log.info (my_nodes)

    restraint_setup = SetupRestraint()
    restraint_setup.restraint_repo()
    restraint_setup.restraint_install()
    restraint_setup.restraint_start()

    job_in = os.environ.get('JOB_NAME')
    if "ipa-user-cli" in job_in:
        if not job_in:
            util.log.error("Failed to find JOB_NAME env variable.")
            sys.exit(1)
        else:
            util.log.info("ipa-user-cli suite identified.")
        job_name = ("ipa-user-cli.xml")
        restraint_job = os.path.join(restraint_loc, job_name)
        host1 = ("1=%s:8081" % my_nodes[0])
        subprocess.check_call(['cat', restraint_job])
        subprocess.check_call(['restraint', '--job', restraint_job, '--host', host1, '-v'])

if __name__ == '__main__':
    beaker_run()
