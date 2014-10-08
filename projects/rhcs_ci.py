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

    """ Sets up the workspace Directory and returns job_name """
    setup_config = SetupConfig()
    setup_config.workspace_dir("WORKSPACE")
    job_name = setup_config.jenkins_job_name("JOB_NAME")
    return job_name

def existing_nodes():
    """ Gets the existing beaker nodes to configure restraint
    on them. Returns a list of existing beaker systems """
    existing_nodes = ExistingNodes("EXISTING_NODES")
    existing_nodes.env_check()
    my_nodes = existing_nodes.identify_nodes()
    return my_nodes

def restraint_setup():

    """ Configures restraint on beaker nodes """
    restraint_setup = Restraint()
    restraint_setup.restraint_repo()
    restraint_setup.remove_rhts_python()
    restraint_setup.restraint_install()
    restraint_setup.restraint_start()
    return restraint_setup

def restraint_location():

    """ Gets restraint job xml location from the current workspace """
    idm_config = ConfigParser.SafeConfigParser()
    idm_config.read("etc/global.conf")
    workspace_option = idm_config.get('global', 'workspace')

    rhcs_config = ConfigParser.SafeConfigParser()
    rhcs_config.read("etc/rhcs.conf")
    restraint_option = rhcs_config.get('global', 'restraint_jobs')
    restraint_loc = os.path.join(workspace_option, restraint_option)
    return restraint_loc

def restraint_single_free(job_name,my_nodes,restraint_loc):

    """calls the restraint command 
    @param:
    job_name is the job_name that is run from jenkins 
    my_nodes is the number of beaker nodes
    restraint_loc is the restraint xml job that will be 
    passed to restraint command
    """

    project configuration file, 
    rhcs_config = ConfigParser.SafeConfigParser()
    rhcs_config.read("etc/rhcs.conf")

    if rhcs_config.has_section(job_name):
        job = rhcs_config.get(job_name, 'job_name')
        restraint_job = os.path.join(restraint_loc, job)
        print restraint_job
    else:
        common.util.log.error("Unable to get job_name")
        sys.exit(1)
    if os.path.exists(restraint_job):
        j = open(restraint_job, 'r').read()
        m = j.replace('hostname1', my_nodes[0])
        f = open(restraint_job, 'w')
        f.write(m)
        f.close()
    else:
        common.util.log.error("Unable to find file")
        sys.exit(2)

    host1 = ("1=%s:8081" % my_nodes[0])
    subprocess.check_call(['cat', restraint_job])
    returncode = subprocess.check_call(['restraint', '-j', restraint_job, '-t', host1])

    return returncode 

def beaker_run():
    
    """ Calls restraint and provides the junit file """
    job_name = get_workspace()
    my_nodes = existing_nodes()
    restraint_inst = restraint_setup()
    restraint_loc = restraint_location()

    rhcs_config = ConfigParser.SafeConfigParser()
    rhcs_config.read("etc/rhcs.conf")
    
    if job_name:    
        rhcs_config.has_section(job_name)
        job_style = ipa_config.get(job_name, 'style')
        job_type = ipa_config.get(job_name, 'type')
    else:
        common.util.log.error("Unable to get job_name")
        sys.exit(1)

    if job_type == "single" and job_style == "free":

        common.util.log.info("Job type is %s and job style is %s" % (job_type, job_style))
        returncode = restraint_single_free(job_name,my_nodes,restraint_loc)
        common.util.log.info("Restraint returned with %r" % returncode)

    else:
        common.util.log.error("Unknown job_style or job_type")
        sys.exit(1)

    restraint_inst.restraint_junit("junit.xml")
