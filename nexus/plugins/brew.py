#!/usr/bin/python

import koji as brew
import os
import os.path
from nexus.lib import factory

pathinfo = brew.PathInfo(topdir='http://download.lab.bos.redhat.com/brewroot')
brew = brew.ClientSession('http://brewhub.devel.redhat.com/brewhub')

class Brew():

    def __init__(self, options, conf_dict):

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


    def list_tagged(self, item):
        builds = brew.listTagged(self.brew_tag, latest=True, package=item, type=None, inherit=True)
        print builds


    def get_latest(self, options, conf_dict):
        fac = factory.Threader()
        fac.gather_results([fac.get_item(self.list_tagged, item) for item in \
                           self.brew_builds])

    #def get_url():

    #def get_builds():
    #    factory.get_item()
    #    factory.gather_results()
