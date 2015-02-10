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


from nexus.lib import logger
from nexus.lib import factory
from nexus.plugins.brew import Brew
from nexus.plugins.git import Git
from nexus.plugins.restraint import Restraint

class CI():

    def __init__(self, options, conf_dict):
        self.provisioner = options.provisioner

    def run(self, options, conf_dict):
        if self.provisioner == "beaker":
            git = Git(options, conf_dict)
            git.get_archive()

            restraint = Restraint(options, conf_dict)
            restraint.run_restraint(options, conf_dict)
            restraint.restraint_junit()
        else:
            logger.log.error("Unknown provisioner")
