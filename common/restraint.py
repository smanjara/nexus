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
import json
from pprint import pprint


class Restraint():
    def __init__(self):
        globalt_config = ConfigParser.SafeConfigParser()
        global_config.read("etc/global.conf")
        util.log.info (global_config.sections())
        self.username = global_config.get('global', 'username')
        self.password = global_config.get('global', 'password')
        self.r_pkgs = global_config.get('restraint', 'remove_pkgs')
        self.i_pkgs = global_config.get('restraint', 'install_pkgs')


    def restraint_repo(self):
        """downloads restraint repo file into /etc/yum.repos.d/"""
        # TODO: check the OS and download its respective repo file instead of
        # hardcoding el6.repo
        # https://github.com/gsr-shanks/ci-utilities/issues/8
        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        #with open("$WORKSPACE/resources.json") as json_file:
      
        
        with open("$WORKSPACE/resources.json") as json_file:
            data = json.load(json_file)
            version = data["family"]
            if version == "RedHatEnterpriseLinux6":
                     repo_url = "http://file.bos.redhat.com/~bpeck/restraint/el6.repo"
                     get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)
            elif version == "RedHatEnterpriseLinux7":
                    repo_url = "http://file.bos.redhat.com/~bpeck/restraint/el7.repo"
                    get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)
            elif version == "RedHatEnterpriseLinux4":
                    repo_url = "http://file.bos.redhat.com/~bpeck/restraint/el4.repo"
                    get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)
            elif version == "RedHatEnterpriseLinux5":
                    repo_url = "http://file.bos.redhat.com/~bpeck/restraint/el5.repo"
                    get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)
            elif version == "Fedora19":
                    repo_url = "http://file.bos.redhat.com/~bpeck/restraint/fc19.repo"
                    get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)
            elif version == "Fedora20":
                    repo_url = "http://file.bos.redhat.com/~bpeck/restraint/fc20.repo"
                    get_repo = ("wget %s -O /etc/yum.repos.d/restraint.repo" % repo_url)
            
            node = data["system"]         

            for node in json_file: 
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

        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(my_nodes[0], username=self.username, password=self.password)
            util.log.info("Executing command %s" % yum_remove)
            stdin, stdout, stderr = ssh.exec_command(yum_remove)
            for line in stdout.read().splitlines():
                if "error" in line:
                    util.log.error('host: %s: %s' % (my_node[0], line))
                    sys.exit(1)
                else:
                    util.log.info('host: %s: %s' % (my_nodes[0], line))

    def restraint_install(self):
        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        yum_install = ("yum install -y %s" % self.i_pkgs)

        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(my_nodes[0], username=self.username,
                        password=self.password)
            util.log.info("Executing command %s" % yum_install)
            stdin, stdout, stderr = ssh.exec_command(yum_install)
            for line in stdout.read().splitlines():
                if "error" in line:
                    util.log.error('host: %s: %s' % (my_node[0], line))
                    sys.exit(1)
                else:
                    util.log.info('host: %s: %s' % (my_nodes[0], line))

    def restraint_start(self):
        resources = ExistingNodes("EXISTING_NODES")
        my_nodes = resources.identify_nodes()

        # TODO: move this service name to config/idm_setup.cfg
        service = ("restraintd")
        start_service = ("service %s start; chkconfig %s on" % (service, service))

        for node in my_nodes:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(my_nodes[0], username=self.username,
                        password=self.password)
            util.log.info("Executing command %s" % start_service)
            stdin, stdout, stderr = ssh.exec_command(start_service)
            for line in stdout.read().splitlines():
                if "error" in line:
                    util.log.error('host: %s: %s' % (my_node[0], line))
                    sys.exit(1)
                else:
                    util.log.info('host: %s: %s' % (my_nodes[0], line))

    def restraint_junit(self, x):
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
