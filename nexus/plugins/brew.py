#!/usr/bin/python

import koji as brew
import os
from nexus.lib import factory

pathinfo = brew.PathInfo(topdir='http://download.lab.bos.redhat.com/brewroot')
brew = brew.ClientSession('http://brewhub.devel.redhat.com/brewhub')

class Brew():

    def __init__(self, options, conf_dict):
        """
        If options are not available through cli then check conf provided.
        """

        if options.tag is None:
            self.brew_tag = conf_dict['brew']['brew_tag']
        else:
            self.brew_tag = options.tag

        if options.arch is None:
            self.brew_arch = conf_dict['brew']['brew_arch']
        else:
            self.brew_arch = options.arch

        if options.loc is None:
            self.build_download_loc = conf_dict['brew']['build_download_loc']
        else:
            self.build_download_loc = options.loc

        if not os.path.exists(self.build_download_loc):
            os.makedirs(self.build_download_loc)

        if options.build is None:
            builds = conf_dict['brew']['brew_builds']
        else:
            builds = options.build
        self.brew_builds = [item.strip() for item in builds.split(',')]

    def download_rpms(self, rpmurl):
        """
        Download rpms using wget in threads.
        """

        import wget
        filename = wget.download(rpmurl, self.build_download_loc)

    def get_tagged(self, item):
        """
        This function constructs the download build URL for each rpm and
        creates a list of all the rpms in each build. This rpms list is then
        passed on to threads along with download_rpms().
        """

        builds = brew.listTagged(self.brew_tag, latest=True, package=item, \
                                type=None, inherit=True)
        for build in builds:
            buildpath = pathinfo.build(build)
            rpms = brew.listRPMs(build['id'], arches=self.brew_arch)
            rpms_list = []
            for rpm in rpms:
                rpmpath = pathinfo.rpm(rpm)
                rpmurl = os.path.join(buildpath, rpmpath)
                rpms_list.append(rpmurl)
                self.download_rpms(rpmurl)
                print ("Downloading %s" % rpmurl)


    def get_latest(self, options, conf_dict):
        """
        Opens thread for each build provided and calls get_tagged()
        """
        fac = factory.Threader()
        fac.gather_results([fac.get_item(self.get_tagged, item) for item in \
                           self.brew_builds])
