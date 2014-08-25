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

#checks if the list is empty
def check_empty_list():
       host_in = os.environ.get('EXISTING_NODES')
       if not host_in:
           print "List is empty!"
           sys.exit(1)

#print the first node as master node
def ipa_topology():
       my_node = tuple(os.environ.get('EXISTING_NODES').split(","))
       if len(my_node) == 1:
            print "I have only %s and it is my MASTER." % my_node[0]
       
            
check_empty_list()
ipa_topology()
