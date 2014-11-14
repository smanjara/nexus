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
import ConfigParser
import StringIO


class ExistingNodes():
    def __init__(self, x):
        self.env = x
        global_config = ConfigParser.SafeConfigParser()
        global_config.read("etc/global.conf")
        self.workspace = global_config.get('global', 'workspace')
        resources_file = os.path.join(self.workspace, "RESOURCES.txt")

    def env_check(self):
        """checks if EXISTING_NODES evn variable is empty or
        not"""

        util.log.info("Checking if %s variable is empty and existence of RESOURCES.txt" % self.env)
        host_in = os.environ.get(self.env)
        if not host_in and not os.path.exists(resources_file):
            util.log.error("ENV list is empty and RESOURCES.txt file not found")
            sys.exit(1)
        else:
            util.log.info("ready to go!")

    def identify_nodes(self):
        """converts list of resources into tuple for further use"""

        host_in = os.environ.get(self.env)

        if not host_in:
            config = StringIO.StringIO()
            config.write('[dummysection]\n')
            config.write(open(resources_file).read())
            config.seek(0, os.SEEK_SET)

            cp = ConfigParser.ConfigParser()
            cp.readfp(config)
            my_nodes = cp.get('dummysection', 'EXISTING_NODES')
            util.log.info("EXISTING_NODES read from RESOURCES.txt")
        else:
            util.log.info("EXISTING_NODES found in env variable.")
            my_nodes = tuple(os.environ.get(self.env).split(","))

        if len(my_nodes) == 1:
            util.log.info("I have only %s and it is my MASTER." % my_nodes[0])
            return my_nodes
        else:
            util.log.info("I have multiple resources")
            return my_nodes
