#!/usr/bin/python
# Copyright (c) 2015 Red Hat, Inc. All rights reserved.
#
# This copyrighted material is made available to anyone wishing
# to use, modify, copy, or redistribute it subject to the terms
# and conditions of the GNU General Public License version 2.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

import os
import sys
import platform
import glob
import subprocess
import shutil
from nexus.lib.factory import SSHClient
from nexus.lib.factory import Threader
from nexus.lib import jenkins
from nexus.lib import logger

class Restraint():

    def __init__(self, options, conf_dict):

        self.username = conf_dict['beaker']['username']
        self.password = conf_dict['beaker']['password']
        nodes = conf_dict['jenkins']['existing_nodes']
        self.existing_nodes = [item.strip() for item in nodes.split(',')]

        self.jenkins_job_name = conf_dict['jenkins']['job_name']
        self.build_repo_tag = os.environ.get("BUILD_REPO_TAG")

    def copy_build_repo(self, host, conf_dict):
        """copy the brew build repo to all the existing nodes"""

        self.build_repo_file = self.build_repo_tag + ".repo"
        self.build_repo_url = os.environ.get("BUILD_REPO_URL")

        logger.log.info("Creating build repo file %s" % self.build_repo_file)
        repo = open(self.build_repo_file, "w")
        repo.write( "[" + self.build_repo_tag + "]\n");
        repo.write( "name=" + self.build_repo_tag + "\n" );
        repo.write( "baseurl=" + self.build_repo_url + "\n" );
        repo.write( "enabled=1\n") ;
        repo.write( "gpgcheck=0\n" );
        repo.write( "skip_if_unavailable=1\n" );
        repo.close()

        source = self.build_repo_file
        destination = "/etc/yum.repos.d/" + source

        logger.log.info("source file is %s" % source)
        logger.log.info("destination file is %s" % destination)

        ssh_c = SSHClient(hostname = host, username = \
                                  self.username, password = self.password)
        ssh_c.CopyFiles(source, destination)

    def my_build_repo(self, host, conf_dict):

        source = self.build_repo
        destination = "/etc/yum.repos.d/my_build.repo"

        logger.log.info("Copying %s to %s on %s" % (source, destination, host))
        ssh_c = SSHClient(hostname = host, username = \
                                  self.username, password = self.password)
        ssh_c.CopyFiles(source, destination)


    def restraint_setup(self, host, conf_dict):
        """
        wget appropriate restraint repo to respective nodes.
        Install restraint rpms and start its service.
        """

        logger.log.info("Checking platform.dist of %s" % host)
        ssh_c = SSHClient(hostname = host, username = \
                                  self.username, password = self.password)
        stdin, stdout, stderr = ssh_c.ExecuteCmd('python -c "import platform; \
                                                 print platform.dist()"')
        dist = stdout.read()
        dist = str(dist).replace('(','').replace(')','').replace("'", "").\
               replace(',','')
        dist = dist.split()
        logger.log.info("Platform distribution for host %s is %s" % (host, dist))
        repo_out = "/etc/yum.repos.d/restraint.repo"

        restraint_repo = conf_dict['restraint'][dist[1]]
        wget_cmd = "wget " + restraint_repo + " -O " + repo_out
        logger.log.info("%s to %s" % (host, wget_cmd))
        stdin, stdout, stderr = ssh_c.ExecuteCmd(wget_cmd)
        for line in stdout.read().splitlines(): logger.log.info(line)

        restraint_remove_rpms = conf_dict['restraint']['remove_rpm']
        remove_cmd = "yum remove -y " + restraint_remove_rpms
        logger.log.info("%s to %s" % (host, remove_cmd))
        stdin, stdout, stderr = ssh_c.ExecuteCmd(remove_cmd)
        for line in stdout.read().splitlines(): logger.log.info(line)

        restraint_install_rpms = conf_dict['restraint']['install_rpm']
        install_cmd = "yum install -y " + restraint_install_rpms
        logger.log.info("%s to %s" % (host, install_cmd))
        stdin, stdout, stderr = ssh_c.ExecuteCmd(install_cmd)
        for line in stdout.read().splitlines(): logger.log.info(line)

        service = ("restraintd")
        start_service_cmd = ("service %s start; chkconfig %s on" % (service, \
                            service))
        logger.log.info("%s to %s" % (host, start_service_cmd))
        stdin, stdout, stderr = ssh_c.ExecuteCmd(start_service_cmd)
        for line in stdout.read().splitlines(): logger.log.info(line)

    def restraint_update_xml(self):

        logger.log.info("Updating %s with existing_node information" % \
                        self.restraint_xml)
        node = 0
        host_num = 1
        host_recipe = []
        while node < len(self.existing_nodes):
            if os.path.exists(self.restraint_xml):
                host_num = str(host_num)
                hostname = ("hostname" + host_num);
                host_num = int(host_num)
                j = open(self.restraint_xml, 'r').read()
                m = j.replace(hostname, (self.existing_nodes[node]))
                f = open(self.restraint_xml, 'w')
                f.write(m)
                f.close()

                mystr = "-t" + " " + str(host_num) + '=' + self.existing_nodes[node]

                host_recipe.append(mystr)
                self.restraint_hosts = " ".join(host_recipe)
                node = node + 1
                host_num = host_num + 1
            else:
                logger.log.error("%s not found" % self.restraint_xml)
                sys.exit(2)

    def execute_restraint(self):
        """
        Check for the length of resources and build appropriate restraint
        command for both single and multi host execution.
        """

        subprocess.check_call(['cat', self.restraint_xml])
        if len(self.existing_nodes) == 1:
            host1 = ("1=%s:8081" % self.existing_nodes[0])
            try:
                subprocess.check_call(['restraint', '-j', \
                    self.restraint_xml, '-t', host1, '-v', '-v'])
            except subprocess.CalledProcessError as e:
                exit(e.returncode)
        else:
            rest_command = "restraint" + " " + "-j" + " " + self.restraint_xml \
                            + " " + self.restraint_hosts + " " + "-v" + " " + "-v"
            logger.log.info(rest_command)
            try:
                subprocess.check_call(rest_command.split(), shell=False)
            except subprocess.CalledProcessError as e:
                exit(e.returncode)

    def restraint_junit(self):
        """convert job.xml to junit.xml"""

        logger.log.info("Converting job.xml to junit")
        job2junit = "/usr/share/restraint/client/job2junit.xml"

        all_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
        latest_dir = max(all_dirs, key=os.path.getmtime)

        job_xml = os.path.join(latest_dir, "job.xml")
        args = ('xsltproc', '/usr/share/restraint/client/job2junit.xml', job_xml)
        p_out = subprocess.PIPE
        p_err = subprocess.PIPE

        p = subprocess.Popen(args,stdout=p_out,stderr=p_err)
        stdout,stderr = p.communicate()

        fd = open("junit.xml", "w")
        fd.write(stdout)
        fd.close()

    def restraint_html(self):
        """get index.html from test directory to workspace"""

        logger.log.info("Get index.html from test directory to workspace")
        index_html = glob.glob("*/index.html")

        if os.path.exists(index_html):

            logger.log.info("index.html found at %s" % index_html)

            src = index_html[0]
            dst = "restraint_results.html"

            shutil.copyfile(src, dst)
        else:
            logger.log.warn("index.html not found.")


    def run_restraint(self, options, conf_dict):
        """
        Call restraint_setup function using threads per host.
        """

        logger.log.info("Running restraint...")
        threads = Threader()

        if options.restraint_xml is None:
            self.jenkins_workspace = conf_dict['jenkins']['workspace']
            self.restraint_xml_loc = conf_dict['restraint_jobs'][self.jenkins_job_name]
            self.restraint_xml = os.path.join(self.jenkins_workspace, \
                                 self.restraint_xml_loc)
            threads.gather_results([threads.get_item(self.restraint_setup, \
                                    host, conf_dict) for host in \
                                    self.existing_nodes])
        else:
            self.restraint_xml = options.restraint_xml
            threads = Threader()
            threads.gather_results([threads.get_item(self.restraint_setup, \
                                    host, conf_dict) for host in \
                                    self.existing_nodes])

        if self.build_repo_tag:
            logger.log.info("BUILD_REPO_TAG found in env")
            logger.log.info("Copying %s to %s" % (self.copy_build_repo, host))
            threads.gather_results([threads.get_item(self.copy_build_repo, \
                                    host, conf_dict) for host in \
                                    self.existing_nodes])
        else:
            logger.log.info("BUILD_REPO_TAG not found in env")

        if options.build_repo:
            logger.log.info("Manual repo to be copied to resources.")
            self.build_repo = options.build_repo
            threads.gather_results([threads.get_item(self.my_build_repo, \
                                   host, conf_dict) for host in \
                                   self.existing_nodes])
        else:
            logger.log.info("No manual repo to be copied to resources.")

        logger.log.info("Using %s" % self.restraint_xml)
        if len(self.existing_nodes) == 1:
            logger.log.info("Found single host in existing_nodes")
            logger.log.info("single node: %s" % self.existing_nodes)
            self.restraint_update_xml()
            self.execute_restraint()
        else:
            logger.log.info("Found multiple hosts in existing_nodes")
            logger.log.info("multiple nodes: %s" % self.existing_nodes)
            self.restraint_update_xml()
            self.execute_restraint()
