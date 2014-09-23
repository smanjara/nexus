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
import ConfigParser
from common_ci import ExistingNodes
from common_ci import SetupRestraint
from config_ci import SetupConfig


def beaker_run():

    setup_config = SetupConfig()
    setup_config.workspace_dir()
    setup_config.jenkins_job_name()
    setup_config.identify_nodes()

    idm_config = ConfigParser.SafeConfigParser()
    idm_config.read("config/idm_setup.cfg")
    workspace_option = idm_config.get('global', 'workspace')
    restraint_option = idm_config.get('beaker', 'restraint_jobs')

    restraint_loc = os.path.join(workspace_option, restraint_option)

    restraint_setup = SetupRestraint()
    restraint_setup.restraint_repo()
    restraint_setup.remove_rhts_python()
    restraint_setup.restraint_install()
    restraint_setup.restraint_start()

    job_in = idm_config.get('global', 'job_name')
    # TODO - change the following hardcoded job_name value to detect from
    # JOB_NAME jenkins variable
    job_name = ("ipa-user-cli.xml")
    restraint_job = os.path.join(restraint_loc, job_name)
    host1 = ("1=%s:8081" % my_nodes[0])
    subprocess.check_call(['cat', restraint_job])
    subprocess.check_call(['restraint', '--job', restraint_job, '--host', host1, '-v'])

if __name__ == '__main__':
    beaker_run()
