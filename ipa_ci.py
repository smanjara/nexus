#!/usr/bin/python
# Copyright (c) 2014 Red Hat, Inc. All rights reserved.
#
# This copyrighted material is made available to anyone wishing
# to use, modify, copy, or redistribute it subject to the terms
# and conditions of the GNU General Public License version 2.
#
# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

import sys
import os
import paramiko
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

username = "root"
password = "whatever"
git_clone = "git clone http://git.app.eng.bos.redhat.com/git/ipa-tests.git"
shared_task = ". env_profile; cd /root/ipa-tests/beaker/ipa-server/shared; make run"

# checks if the list is empty
def check_empty_list():
    LOG.info("Checking if EXISTING_NODES variable is empty")
    host_in = os.environ.get('EXISTING_NODES')
    if not host_in:
        LOG.error("List is empty!")
        sys.exit(1)
    else:
        LOG.info("EXISTING_NODES list is not empty!")

# print the first node as master node
def ipa_aio():
    my_node = tuple(os.environ.get('EXISTING_NODES').split(","))
    if len(my_node) == 1:
        LOG.info("I have only %s and it is my MASTER." % my_node[0])

        # creats a new SSHClient object and then calls connect()
        ssh = paramiko.SSHClient()

        # "paramiko.AutoAddPolicy()" which will auto-accept unknown keys.
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(my_node[0], username=username,
                    password=password)
        LOG.info("Executing command %s" % git_clone)
        stdin, stdout, stderr = ssh.exec_command(git_clone)
        for line in stdout.read().splitlines():
            LOG.info('host: %s: %s' % (my_node[0], line))

        stdin, stdout, stderr = ssh.exec_command(shared_task)
        for line in stdout.read().splitlines():
            if "FAIL" in line:
                LOG.error('host: %s: %s' % (my_node[0], line))
            else:
                LOG.info('host: %s: %s' % (my_node[0], line))

        ipa_usercli_task = ". env_profile; cd /root/ipa-tests/beaker/ipa-server/acceptance/ipa-user-cli/adduser/; make run"
        stdin, stdout, stderr = ssh.exec_command(ipa_usercli_task)
        for line in stdout.read().splitlines():
            if "FAIL" in line:
                LOG.error('host: %s: %s' % (my_node[0], line))
            else:
                LOG.info('host: %s: %s' % (my_node[0], line))

        ssh.close()
    else:
        LOG.info("Multiple nodes detected.")

check_empty_list()
ipa_aio()
