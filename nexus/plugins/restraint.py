#!/usr/bin/python

import os
import sys
import platform
import glob
from nexus.lib.factory import SSHClient
from nexus.lib.factory import Threader
from nexus.lib import jenkins

class Restraint():

    def __init__(self, options, conf_dict):

        self.username = conf_dict['beaker']['username']
        self.password = conf_dict['beaker']['password']
        nodes = conf_dict['jenkins']['existing_nodes']
        self.existing_nodes = [item.strip() for item in nodes.split(',')]


    def copy_build_repo(self):
        """copy the brew build repo to all the existing nodes"""

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

        source = build_repo_file
        destination = "/etc/yum.repos.d/" + source

        return source, destination


    def restraint_setup(self, host, conf_dict):
        """
        wget appropriate restraint repo to respective nodes.
        Install restraint rpms and start its service.
        """

        print host
        ssh_c = SSHClient(hostname = host, username = \
                                  self.username, password = self.password)
        stdin, stdout, stderr = ssh_c.ExecuteCmd('python -c "import platform; \
                                                 print platform.dist()"')
        dist = stdout.read()
        dist = str(dist).replace('(','').replace(')','').replace("'", "").\
               replace(',','')
        dist = dist.split()
        repo_out = "/etc/yum.repos.d/restraint.repo"

        restraint_repo = conf_dict['restraint'][dist[1]]
        wget_cmd = "wget " + restraint_repo + " -O " + repo_out
        stdin, stdout, stderr = ssh_c.ExecuteCmd(wget_cmd)
        for line in stdout.read().splitlines(): print line

        restraint_remove_rpms = conf_dict['restraint']['remove_rpm']
        remove_cmd = "yum remove -y " + restraint_remove_rpms
        stdin, stdout, stderr = ssh_c.ExecuteCmd(remove_cmd)
        for line in stdout.read().splitlines(): print line

        restraint_install_rpms = conf_dict['restraint']['install_rpm']
        install_cmd = "yum install -y " + restraint_install_rpms
        stdin, stdout, stderr = ssh_c.ExecuteCmd(install_cmd)
        for line in stdout.read().splitlines(): print line

        service = ("restraintd")
        start_service_cmd = ("service %s start; chkconfig %s on" % (service, service))
        stdin, stdout, stderr = ssh_c.ExecuteCmd(start_service_cmd)
        for line in stdout.read().splitlines(): print line

        source, destination = self.copy_build_repo()
        ssh_c.CopyFiles(source, destination)


    def run_restraint(self, conf_dict):
        """
        Call restraint_setup function using threads per host.
        """

        print self.existing_nodes
        threads = Threader()
        threads.gather_results([threads.get_item(self.restraint_setup, host, conf_dict) for host in \
                            self.existing_nodes])
