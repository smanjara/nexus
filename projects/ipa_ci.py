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

def get_workspace():
    global job_name
    setup_config = SetupConfig()
    setup_config.workspace_dir("WORKSPACE")
    job_name = setup_config.jenkins_job_name("JOB_NAME")

def existing_nodes():
    global my_nodes
    existing_nodes = ExistingNodes("EXISTING_NODES")
    existing_nodes.env_check()
    my_nodes = existing_nodes.identify_nodes()

def restraint_setup():
    restraint_setup = Restraint()
    restraint_setup.restraint_repo()
    restraint_setup.remove_rhts_python()
    restraint_setup.restraint_install()
    restraint_setup.restraint_start()

def restraint_location():
    global restraint_loc
    idm_config = ConfigParser.SafeConfigParser()
    idm_config.read("etc/global.conf")
    workspace_option = idm_config.get('global', 'workspace')

    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")
    restraint_option = ipa_config.get('global', 'restraint_jobs')

    restraint_loc = os.path.join(workspace_option, restraint_option)

def restraint_single_free():
    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")

    if ipa_config.has_section(job_name):
        job = ipa_config.get(job_name, 'job_name')
        restraint_job = os.path.join(restraint_loc, job)
        print restraint_job
    else:
        common.util.log.error("Unable to get job_name")
        sys.exit(1)

    j = open(restraint_job, 'r').read()
    m = j.replace('hostname1', my_nodes[0])
    f = open(restraint_job, 'w')
    f.write(m)
    f.close()

    host1 = ("1=%s:8081" % my_nodes[0])

    subprocess.check_call(['cat', restraint_job])
    subprocess.check_call(['restraint', '-j', restraint_job, '-t', host1])

def junit_results():
    restraint_setup = Restraint()
    restraint_setup.restraint_junit("junit.xml")

def beaker_run():
    get_workspace()
    existing_nodes()
    restraint_setup()
    restraint_location()

    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")
    if 'job_name' in globals():
        ipa_config.has_section(job_name)
        job_style = ipa_config.get(job_name, 'style')
        job_type = ipa_config.get(job_name, 'type')
    else:
        common.util.log.error("Unable to get job_name")
        sys.exit(1)

    if job_type == "single" and job_style == "free":
        common.util.log.info("Job type is %s and job style is %s" % (job_type, job_style))
        restraint_single_free()
    else:
        common.util.log.error("Unknown job_style or job_type")
        sys.exit(1)

    junit_results()
