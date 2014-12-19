#!/usr/bin/python
# -*- coding: utf-8 -*-
#######################################################################
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
#######################################################################
import ConfigParser
import xmlrpclib
import os
import re
import shutil
import util

class Errata():
    """This class is to get values from errata"""

    def __init__(self, errata_id=None, errata_rel_ver=None):
        """Initialize connection to xmlrpc server using xmlrpc_url. errata_id
        is required for initialization, if not given then the script will exit.
        """

        if errata_id == None:
            self.errata_id = os.environ.get("errata_id")
        else:
            self.errata_id = errata_id

        if self.errata_id == None:
            util.log.error("Value for errata_id not found")
            raise ValueError

        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("etc/global.conf")
        self.workspace_loc = idm_config.get('global', 'workspace')

        errata = ConfigParser.SafeConfigParser()
        errata.read("etc/ipa.conf")
        errata_config = errata.get('global', 'errata_config')
        self.errata_config_loc = os.path.join(self.workspace_loc, errata_config)
        self.errata_yamls_loc = errata.get('global', 'errata_yamls')

        e = ConfigParser.SafeConfigParser()
        e.read(self.errata_config_loc)
        self.xmlrpc_url = e.get('errata-info', 'xmlrpc-url')
        self.download_loc = e.get('errata-info', 'download_loc')
        self.mount_base = e.get('errata-info', 'mount_base')

        try:
            self.xmlrpc_url and self.errata_id
        except NameError:
            print "xmlrpc_url or errata_id is not defined"

        if errata_rel_ver == None:
            self.errata_release_version()
        else:
            self.errata_release_version = errata_rel_ver

        self.errata_yaml_template = e.get('errata-info', self.errata_rel_ver)

    def getPackagesURL(self):
        """The response we get from xmlrpc for getErrataPackages is with the
        mount location which is defined in errata.conf. This function replaces
        mount location with http download URL.
        """

        et_rpc_proxy = xmlrpclib.ServerProxy(self.xmlrpc_url)
        response = et_rpc_proxy.getErrataPackages(self.errata_id)

        response = [w.replace(self.mount_base, self.download_loc) for w in \
                    response]
        response = set(response)
        return response

    def errata_release_version(self):
        """It is important to get release_version for the errata. We plan to
        use templates per release version for scalability which would be
        specified in errata.conf of your project repository. So depending on
        the release_version template would be selected.
        """

        et_rpc_proxy = xmlrpclib.ServerProxy(self.xmlrpc_url)
        errata_rel = et_rpc_proxy.get_base_packages_rhts(self.errata_id)
        errata_release = [i['rhel_version'] for i in errata_rel if \
                            'rhel_version' in i]
        self.errata_rel_ver = errata_release[0]
        return self.errata_rel_ver

    def errata_yaml(self):
        """Template yaml once identified needs to be copied with errata id as
        part of the yaml file name so that it is easy to identify.
        """

        errata_id = str(self.errata_id)
        self.errata_release_version()

        util.log.info ("Errata #: %s" %self.errata_id)
        util.log.info ("Errata config location: %s" %self.errata_config_loc)
        errata_yaml_template = os.path.join(self.workspace_loc, \
                                self.errata_yamls_loc, \
                                self.errata_yaml_template)
        util.log.info ("%s YAML job template for Errata # %s: %s" % \
                        (self.errata_rel_ver, errata_id, errata_yaml_template))

        errata_new_yaml = self.errata_yaml_template.replace('ERRATA', errata_id)
        errata_yaml = os.path.join(self.workspace_loc, self.errata_yamls_loc, \
                                    errata_new_yaml)
        util.log.info ("%s YAML job for Errata # %s: %s" % (self.errata_rel_ver, \
                        errata_id, errata_yaml))

        try:
            shutil.copyfile(errata_yaml_template, errata_yaml)
        except IOError as ioerr:
            print "There was an IO Error", ioerr
            raise
        else:
            util.log.info("Successfully copied %s to %s" % (errata_yaml_template, errata_yaml))
            return 0
