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

import os
import wget
import xmlrpclib
from nexus.lib import factory
from nexus.lib import logger

class Errata():

    def __init__(self, options, conf_dict):

        self.errata_id = os.environ.get("errata_id")
        logger.log.info("Errata id is %s" % self.errata_id)

        self.errata_xmlrpc = conf_dict['errata']['xmlrpc_url']
        self.errata_download = conf_dict['errata']['download_devel']

        if options.errata_loc is None:
            self.errata_download_loc = conf_dict['errata']['build_download_loc']
        else:
            self.errata_download_loc = options.errata_loc
        self.errata_mount_base = conf_dict['errata']['mount_base']

        if not os.path.exists(self.errata_download_loc):
            os.makedirs(self.errata_download_loc)

        try:
            self.errata_id and self.errata_xmlrpc
        except NameError:
            print "xmlrpc_url or errata_id is not defined"

    def get_package_url(self):
        """ This function returns the response received from xmlrpc server.
        In this case, it returns build URL.
        """

        et_rpc_proxy = xmlrpclib.ServerProxy(self.errata_xmlrpc)
        response = et_rpc_proxy.getErrataPackages(self.errata_id)

        response = [w.replace(self.errata_mount_base, self.errata_download) for w in response]
        response = set(response)
        return response

    def download_rpms(self, rpm_url):
        """ Download builds using wget """

        filename = wget.download(rpm_url, self.errata_download_loc)

    def download_errata_builds(self):
        """ Function to iterate through the rpm set
        and call download_rpms function
        """

        rpm_set = self.get_package_url()

        for rpm_url in rpm_set:
            logger.log.info(rpm_url)
            rpm_name = os.path.basename(rpm_url)
            logger.log.info("Downloading %s" % rpm_url)
            self.download_rpms(rpm_url)
