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
import glob
from common.nodes import ExistingNodes
from common.restraint import Restraint
from common.config import SetupConfig
from lxml import etree
from tools.RunTask import SSHClient


def get_workspace():

    """ Sets up the workspace Directory and returns job_name """
    setup_config = SetupConfig()
    workspace = setup_config.workspace_dir("WORKSPACE")
    return workspace

def get_job_name():
    setup_config = SetupConfig()
    job_name = setup_config.jenkins_job_name("JOB_NAME")
    return job_name

def existing_nodes():

    """ Gets the existing beaker nodes to configure restraint
    on them. Returns a list of existing beaker systems"""
    existing_nodes = ExistingNodes("EXISTING_NODES")
    existing_nodes.env_check()
    my_nodes = existing_nodes.identify_nodes()
    return my_nodes

def copy_repo(my_nodes):

    """copy the brew build repo in all the existing nodes"""
    #TODO Move this to common as this would be required for other teams
    global_config = ConfigParser.SafeConfigParser()
    global_config.read("etc/global.conf")
    username = global_config.get('global', 'username')
    password = global_config.get('global', 'password')

    build_repo_tag = os.environ.get("BUILD_REPO_TAG")
    build_repo_file = build_repo_tag + ".repo"
    build_repo_url = os.environ.get("BUILD_REPO_URL")

    repo = open(build_repo_file, "w")
    repo.write( "[" + build_repo_tag + "]\n");
    repo.write( "name=" + build_repo_tag + "\n" );
    repo.write( "baseurl=" + build_repo_url + "\n" );
    repo.write( "enabled=1\n") ;
    repo.write( "gpgcheck=0\n" );
    repo.write( "skip_if_unavailable=1\n" );
    repo.close()

    repo_list = glob.glob("jenkins*.repo")
    source = repo_list[0]
    destination = "/etc/yum.repos.d/" + repo_name

    #TODO use threads instead of for loop
    for node in my_nodes:
        client = SSHClient(node, 22, username, password)
        client.CopyFiles(source, destination)

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
    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/global.conf")
    workspace_option = ipa_config.get('global', 'workspace')

    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")
    restraint_option = ipa_config.get('global', 'restraint_jobs')
    restraint_loc = os.path.join(workspace_option, restraint_option)
    return restraint_loc

def restraint_single_free(job_name,my_nodes,restraint_loc):

    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")

    #TODO This loop should be moved to common since the same
    # is used in restraint_multi_free()
    if ipa_config.has_section(job_name):
        job = ipa_config.get(job_name, 'job_name')
        print job
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
    returncode = subprocess.check_call(['restraint', '-j', restraint_job, '-t', host1, '-v', '-v'])

    return returncode

def restraint_multi_free(job_name,my_nodes,restraint_loc):

    """Executes restraint command for multi host testing"""
    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")

    #TODO Check restraint_single_free()
    if ipa_config.has_section(job_name):
        job = ipa_config.get(job_name, 'job_name')
        print job
        restraint_job = os.path.join(restraint_loc, job)
        print restraint_job
    else:
        common.util.log.error("Unable to get job_name")
        sys.exit(1)

    node = 0
    host_num = 1
    host_recipe = []
    while node < len(my_nodes):
        if os.path.exists(restraint_job):
            host_num = str(host_num)
            hostname = ("hostname" + host_num);
            host_num = int(host_num)
            j = open(restraint_job, 'r').read()
            m = j.replace(hostname, (my_nodes[node]))
            f = open(restraint_job, 'w')
            f.write(m)
            f.close()

            mystr =  "-t" + " " + str(host_num) + '=' + my_nodes[node]

            host_recipe.append(mystr)
            rest_hosts = " ".join(host_recipe)
            node = node + 1
            host_num = host_num + 1

        else:
            common.util.log.error("Unable to find file")
            sys.exit(2)
    else:
        print "Done iterating through my_nodes"

    subprocess.check_call(['cat', restraint_job])
    rest_command = "restraint" + " " + "-j" + " " + restraint_job + " " + rest_hosts + " " + "-v" + " " + "-v"
    returncode = subprocess.check_call(rest_command.split(), shell=False)

def beaker_run():

    """ Runs the restraint command with the xml file and provides the junit file """
    workspace = get_workspace()
    job_name = get_job_name()
    my_nodes = existing_nodes()
    copy_repo_file = copy_repo(my_nodes)
    restraint_inst = restraint_setup()
    restraint_loc = restraint_location()

    ipa_config = ConfigParser.SafeConfigParser()
    ipa_config.read("etc/ipa.conf")

    if job_name:
        ipa_config.has_section(job_name)
        job_style = ipa_config.get(job_name, 'style')
        job_type = ipa_config.get(job_name, 'type')
    else:
        common.util.log.error("Unable to get job_name")
        sys.exit(1)

    if job_type == "single" and job_style == "free":
        common.util.log.info("Job type is %s and job style is %s" % (job_type, job_style))
        returncode = restraint_single_free(job_name, my_nodes,restraint_loc)
        common.util.log.info("Restraint returned with %r" % returncode)
    elif job_type == "multi" and job_style == "free":
        common.util.log.info("Job type is %s and job style is %s" % (job_type, job_style))
        returncode = restraint_multi_free(job_name, my_nodes, restraint_loc)
        common.util.log.info("Restraint returned with %r" % returncode)
    else:
        common.util.log.error("Unknown job_style or job_type")
        sys.exit(1)

    restraint_inst.restraint_junit("junit.xml")
