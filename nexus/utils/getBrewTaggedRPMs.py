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

"""
This tool downloads the latest build from brew based on the tag, rpm name
and download to location provided as arguments.
"""

import koji as brew
import os.path
import urllib2
import argparse
import json

pathinfo = brew.PathInfo(topdir='http://download.lab.bos.redhat.com/brewroot')
brew = brew.ClientSession('http://brewhub.devel.redhat.com/brewhub')

parser = argparse.ArgumentParser(description='This tool downloads the latest \
                                builds from brew based on its tag, rpm name \
                                and download to location provided as part of \
                                its arguments.')
# Parse options
required = parser.add_argument_group('required arguments')
required.add_argument('--brew-tag', help='brew tag', required=True)
required.add_argument('--pkg', help='pkg name', required=True)
parser.add_argument('--arch', help='Machine arch. Defaults to all it not \
                    provided')
required.add_argument('--location', help='Absolute path of download \
                        to directory', required=True)
args = parser.parse_args()

tag = args.brew_tag
pkg = args.pkg
arch = args.arch

download_dir = args.location
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Lists the latest build for the brew tag and package name provided as
# arguments
builds = brew.listTagged(tag, latest=True, package=pkg, type=None,
inherit=True)

for build in builds:
    buildpath = pathinfo.build(build)

    # Lists latest RPMs
    rpms = brew.listRPMs(build['id'], arches=arch)

    for rpm in rpms:
        rpmpath = pathinfo.rpm(rpm)
        rpmurl = os.path.join(buildpath, rpmpath)
        rpmname = os.path.join(download_dir,rpmurl.split('/')[-1])

        # Download latest RPMs
        u = urllib2.urlopen(rpmurl)
        f = open(rpmname, 'wb')
        f.write(u.read())
        f.close()

        # Print information
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print("Downloading: {0} Bytes: {1}".format(rpmurl, file_size))
        print(rpmname)
