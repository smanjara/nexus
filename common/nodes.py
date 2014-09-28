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
import util


# Username and Password for test resources
# TODO: move this to config/idm_setup.cfg
# https://github.com/gsr-shanks/ci-utilities/issues/16
username = "root"
password = "whatever"

class ExistingNodes():

    def env_check(self):
        """checks if EXISTING_NODES evn variable is empty or
        not"""
        util.log.info("Checking if EXISTING_NODES variable is empty")
        host_in = os.environ.get('EXISTING_NODES')
        if not host_in:
            util.log.error("List is empty!")
            sys.exit(1)
        else:
            util.log.info("EXISTING_NODES list is not empty ... ready to go!")

    def node_check(self):
        """converts list of resources into tuple for further use"""
        my_nodes = tuple(os.environ.get('EXISTING_NODES').split(","))
        if len(my_nodes) == 1:
            util.log.info("I have only %s and it is my MASTER." % my_nodes[0])
            return my_nodes
        else:
            util.log.info("I have multiple resources")
            return my_nodes
