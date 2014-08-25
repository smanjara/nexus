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

def check_empty_list():
    host_in = os.environ.get('EXISTING_NODES')
    if len(host_in) == 0:
        print "List is empty!"
        sys.exit()

my_node = tuple(os.environ.get('EXISTING_NODES').split(","))
def ipa_topology():
    if len(my_node) == 1:
        print "I have only %s and it is my MASTER." % my_node[0]

check_empty_list()
ipa_topology()
