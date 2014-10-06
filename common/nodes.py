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


class ExistingNodes():
    def __init__(self, x):
        self.env = x

    def env_check(self):
        """checks if EXISTING_NODES evn variable is empty or
        not"""

        util.log.info("Checking if %s variable is empty" % self.env)
        host_in = os.environ.get(self.env)
        if not host_in:
            util.log.error("List is empty!")
            sys.exit(1)
        else:
            util.log.info("%s list is not empty ... ready to go!" % self.env)

    def identify_nodes(self):
        """converts list of resources into tuple for further use"""
        my_nodes = tuple(os.environ.get(self.env).split(","))
        if len(my_nodes) == 1:
            util.log.info("I have only %s and it is my MASTER." % my_nodes[0])
            #print my_nodes
            return my_nodes
        else:
            util.log.info("I have multiple resources")
            return my_nodes

        # TODO: need to work on configParser module and its usage in
        # ci-utilities
        #
        #ipa_config = ConfigParser.SafeConfigParser()
        #ipa_config.read("etc/ipa_setup.cfg")
        #util.log.info (ipa_config.sections())
        #util.log.info (my_nodes)

        #ipa_config.set('restraint_xml', 'master', my_nodes[0])

        #with open('etc/ipa_setup.cfg', 'wb') as ipa_setup_config:
        #    ipa_config.write(ipa_setup_config)
