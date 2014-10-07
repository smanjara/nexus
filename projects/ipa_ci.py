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
import string
import common.util
import subprocess
import ConfigParser
from common.nodes import ExistingNodes
from common.restraint import Restraint
from common.config import SetupConfig


def beaker_run():

    setup_config = SetupConfig()
    setup_config.workspace_dir("WORKSPACE")
    setup_config.jenkins_job_name("JOB_NAME")

    existing_nodes = ExistingNodes("EXISTING_NODES")
    existing_nodes.env_check()
    my_nodes = existing_nodes.identify_nodes()

    idm_config = ConfigParser.SafeConfigParser()
    idm_config.read("etc/global.conf")
    workspace_option = idm_config.get('global', 'workspace')

    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")
    restraint_option = ipa_config.get('global', 'restraint_jobs')

    restraint_loc = os.path.join(workspace_option, restraint_option)

    restraint_setup = Restraint()
    restraint_setup.restraint_repo()
    restraint_setup.remove_rhts_python()
    restraint_setup.restraint_install()
    restraint_setup.restraint_start()

    # ~~~~~ Project specific section begins ~~~~~
    #TODO: remove the hardcoded values below and make it generic
    job_name = ipa_config.get('ipa_user_cli', 'job_name')
    restraint_job = os.path.join(restraint_loc, job_name)
    print restraint_job

    j = open(restraint_job, 'r').read()
    m = j.replace('hostname1', my_nodes[0])
    f = open(job_name, 'w')
    f.write(m)
    f.close()

    host1 = ("1=%s:8081" % my_nodes[0])

    subprocess.check_call(['cat', job_name])
    subprocess.check_call(['restraint', '-j', job_name, '-t', host1])
    # ~~~~~ Project specific section ends ~~~~~

    restraint_setup.restraint_junit("junit.xml")

if __name__ == '__main__':
    beaker_run()
