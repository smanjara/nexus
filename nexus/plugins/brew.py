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

import koji as brew
import os
from nexus.lib import factory
from nexus.lib import logger

pathinfo = brew.PathInfo(topdir='http://download.lab.bos.redhat.com/brewroot')
brew = brew.ClientSession('http://brewhub.devel.redhat.com/brewhub')

class Brew():

    def __init__(self, options, conf_dict):
        """
        If options are not available through cli then check conf provided.
        """

        if options.tag is None:
            logger.log.info("No brew-tag provided as option. Checking conf file...")
            self.brew_tag = conf_dict['brew']['brew_tag']
            logger.log.info("brew-tag from conf file is %s" % self.brew_tag)
        else:
            self.brew_tag = options.tag
            logger.log.info("brew-tag from cli is %s" % self.brew_tag)

        if options.arch is None:
            logger.log.info("No build arch provided as option. Checking conf file...")
            self.brew_arch = conf_dict['brew']['brew_arch']
            logger.log.info("build arch from conf file is %s" % self.brew_arch)
        else:
            self.brew_arch = options.arch
            logger.log.info("build arch from cli is %s" % self.brew_arch)

        if options.loc is None:
            logger.log.info("No download builds to location provided as option.\
                            Checking conf file...")
            self.build_download_loc = conf_dict['brew']['build_download_loc']
            logger.log.info("download location from conf file is %s" % self.build_download_loc)
        else:
            self.build_download_loc = options.loc
            logger.log.info("download location from cli is %s" % self.build_download_loc)

        if not os.path.exists(self.build_download_loc):
            logger.log.info("Build download location does not exist, creating %s" \
                            % self.build_download_loc)
            os.makedirs(self.build_download_loc)

        if options.build is None:
            builds = conf_dict['brew']['brew_builds']
        else:
            builds = options.build
        self.brew_builds = [item.strip() for item in builds.split(',')]
        logger.log.info("Builds to download: %s" % self.brew_builds)

    def download_rpms(self, rpmurl):
        """
        Download rpms using wget in threads.
        """

        import wget
        filename = wget.download(rpmurl, self.build_download_loc)

    def get_tagged(self, item, conf_dict):
        """
        This function constructs the download build URL for each rpm and
        creates a list of all the rpms in each build. This rpms list is then
        passed on to threads along with download_rpms().
        """

        builds = brew.listTagged(self.brew_tag, latest=True, package=item, \
                                type=None, inherit=True)
        for build in builds:
            buildpath = pathinfo.build(build)
            arches_noarch = (self.brew_arch, "noarch")
                rpms = brew.listRPMs(build['id'], arches=arches_noarch)
                rpms_list = []
                for rpm in rpms:
                    rpmpath = pathinfo.rpm(rpm)
                    rpmurl = os.path.join(buildpath, rpmpath)
                    rpms_list.append(rpmurl)
                    self.download_rpms(rpmurl)
                    logger.log.info("Downloading %s" % rpmurl)


    def get_latest(self, options, conf_dict):
        """
        Opens thread for each build provided and calls get_tagged()
        """
        fac = factory.Threader()
        fac.gather_results([fac.get_item(self.get_tagged, item, conf_dict) for item in \
                           self.brew_builds])
