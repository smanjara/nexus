#!/usr/bin/python
# Copyright (C) 2014 Red Hat Inc. All rights reserved.
# Author: Gowrishankar Rajaiyan <gsr@redhat.com>
#
# This copyrighted material is made available to anyone wishing
# to use, modify, copy, or redistribute it subject to the terms
# and conditions of the GNU General Public License version 2.

"""
This tool downloads the latest build from koji based on the tag, rpm name
and download to location provided as arguments.
"""

import koji
import os.path
import urllib2
import argparse
import json

pathinfo = koji.PathInfo(topdir='https://kojipkgs.fedoraproject.org')
koji = koji.ClientSession('http://koji.fedoraproject.org/kojihub')

parser = argparse.ArgumentParser(description='This tool downloads the latest \
                                builds from koji based on its tag, rpm name \
                                and download to location provided as part of \
                                its arguments.')
# Parse options
required = parser.add_argument_group('required arguments')
required.add_argument('--koji-tag', help='koji tag', required=True)
required.add_argument('--pkg', help='pkg name', required=True)
parser.add_argument('--arch', help='Machine arch. Defaults to all it not \
                    provided')
required.add_argument('--location', help='Absolute path of download \
                        to directory', required=True)
args = parser.parse_args()

tag = args.koji_tag
pkg = args.pkg
arch = args.arch

download_dir = args.location
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Lists the latest build for the koji tag and package name provided as
# arguments
builds = koji.listTagged(tag, latest=True, package=pkg, type=None,
inherit=True)

for build in builds:
    buildpath = pathinfo.build(build)

    # Lists latest RPMs
    rpms = koji.listRPMs(build['id'], arches=arch)

    for rpm in rpms:
        rpmpath = pathinfo.rpm(rpm)
        rpmurl = os.path.join(buildpath, rpmpath)
        print rpmurl
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
