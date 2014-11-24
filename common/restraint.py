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
from common.nodes import ExistingNodes
from common.config import SetupConfig
import ConfigParser


class Restraint():
    def __init__(self):
        global_config = ConfigParser.SafeConfigParser()
        global_config.read("etc/global.conf")
        util.log.info (global_config.sections())
        self.username = global_config.get('global', 'username')
        self.password = global_config.get('global', 'password')
        self.r_pkgs = global_config.get('restraint', 'remove_pkgs')
        self.i_pkgs = global_config.get('restraint', 'install_pkgs')


    def restraint_repo(self):
        """downloads restraint repo file into /etc/yum.repos.d/"""

        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        global_config = ConfigParser.RawConfigParser()
        global_config.read("etc/global.conf")
        rhel6_restraint_repo = global_config.get('restraint', 'rhel6_restraint_repo')
        rhel7_restraint_repo = global_config.get('restraint', 'rhel7_restraint_repo')

        if "rhel6" in job_name:
            repo_url = rhel6_restraint_repo
        elif "rhel7" in job_name:
            repo_url = rhel7_restraint_repo

        get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)

        #TODO use threads instead of for loop
        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(node, username=self.username,
                        password=self.password)
            util.log.info("Executing command %s" % get_repo)
            stdin, stdout, stderr = ssh.exec_command(get_repo)
            for line in stdout.read().splitlines():
                util.log.info('host: %s: %s' % (node, line))

    def remove_rhts_python(self):
        """remove rhts-python as it conflicts with restraint-rhts"""

        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        yum_remove = ("yum remove -y %s" % self.r_pkgs)

        #TODO use threads instead of for loop
        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(node, username=self.username, password=self.password)
            util.log.info("Executing command %s" % yum_remove)
            stdin, stdout, stderr = ssh.exec_command(yum_remove)
            for line in stdout.read().splitlines():
                if "error" in line:
                    util.log.error('host: %s: %s' % (node, line))
                    sys.exit(1)
                else:
                    util.log.info('host: %s: %s' % (node, line))

    def restraint_install(self):
        """Installs all the packages required for restraint"""

        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        yum_install = ("yum install -y %s" % self.i_pkgs)

        #TODO use threads instead of for loop
        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(node, username=self.username,
                        password=self.password)
            util.log.info("Executing command %s" % yum_install)
            stdin, stdout, stderr = ssh.exec_command(yum_install)
            for line in stdout.read().splitlines():
                if "error" in line:
                    util.log.error('host: %s: %s' % (node, line))
                    sys.exit(1)
                else:
                    util.log.info('host: %s: %s' % (node, line))

    def restraint_start(self):
        """start the restraint service and chkconfig on"""

        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        # TODO: move this service name to config/idm_setup.cfg
        service = ("restraintd")
        start_service = ("service %s start; chkconfig %s on" % (service, service))

        #TODO use threads instead of for loop
        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(node, username=self.username,
                        password=self.password)
            util.log.info("Executing command %s" % start_service)
            stdin, stdout, stderr = ssh.exec_command(start_service)
            for line in stdout.read().splitlines():
                if "error" in line:
                    util.log.error('host: %s: %s' % (node, line))
                    sys.exit(1)
                else:
                    util.log.info('host: %s: %s' % (node, line))

    def restraint_junit(self, x):
        """convert job.xml to junit.xml"""

        self.junit_xml = x
        job2junit = "/usr/share/restraint/client/job2junit.xml"

        all_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
        latest_dir = max(all_dirs, key=os.path.getmtime)

        job_xml = os.path.join(latest_dir, "job.xml")
        junit_xml = self.junit_xml

        args = ('xsltproc', '/usr/share/restraint/client/job2junit.xml', job_xml)
        p_out = subprocess.PIPE
        p_err = subprocess.PIPE

        p = subprocess.Popen(args,stdout=p_out,stderr=p_err)
        stdout,stderr = p.communicate()

        fd = open(junit_xml, "w")
        fd.write(stdout)
        fd.close()

