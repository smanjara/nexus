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
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class ExistingNodes():

    def _env_check(self):
        LOG.info("Checking if EXISTING_NODES variable is empty")
        host_in = os.environ.get('EXISTING_NODES')
        if not host_in:
            LOG.error("List is empty!")
            sys.exit(1)
        else:
            LOG.info("EXISTING_NODES list is not empty ... ready to go!")

