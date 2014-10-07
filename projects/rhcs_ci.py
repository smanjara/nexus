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
from lxml import etree


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
    print "workspace_option = ",workspace_option


    rhcs_config = ConfigParser.SafeConfigParser()
    rhcs_config.read("etc/rhcs.conf")
    restraint_option = rhcs_config.get('global', 'restraint_jobs')
    print "restraint_option = ", restraint_option
    

    restraint_loc = os.path.join(workspace_option, restraint_option)
    print "restraint_loc=", restraint_loc
    restraint_setup = Restraint()
    restraint_setup.restraint_repo()
    restraint_setup.remove_rhts_python()
    restraint_setup.restraint_install()
    restraint_setup.restraint_start()

    #TODO: remove the hardcoded values below and make it generic
    job_name = rhcs_config.get('test_suite', 'job_name')
    restraint_job = os.path.join(restraint_loc, job_name)
    print "restraint_job = ",restraint_job
    
    # verify if the file exists 
    if os.path.exists(restraint_job):
        tree = etree.parse(restraint_job)
        root = tree.getroot()
        id = tree.xpath('./recipeSet/recipe[@id="1"]/task/params/param')
        id[0].set("value", my_nodes[0])
        tree.write(job_name)
        

    host1 = ("1=%s:8081" % my_nodes[0])
    print host1

    subprocess.check_call(['cat', job_name])
    subprocess.check_call(['restraint', '-j', job_name, '-t', host1])

    restraint_setup.restraint_junit("junit.xml")


if __name__ == '__main__':
     beaker_run()
