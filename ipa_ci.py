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
from common_ci import ExistingNodes

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def beaker_run():
    resources = ExistingNodes()
    resources.env_check()

    my_nodes = resources.node_check()
    LOG.info (my_nodes)

if __name__ == '__main__':
    beaker_run()
