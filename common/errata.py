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

class Errata():
    """This class is to get values from errata"""

    def __init__(self, errata_id):
        """Initialize connection to xmlrpc server using xmlrpc_url. errata_id is required
        for initialization, if not given then the script will exit.
        """
        self.errata_id = errata_id

        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("etc/global.conf")
        workspace_loc = idm_config.get('global', 'workspace')

        errata = ConfigParser.SafeConfigParser()
        errata.read("etc/ipa.conf")
        errata_config = errata.get('global', 'errata_config')
        errata_config_loc = os.path.join(workspace_loc, errata_config)

        xmlrpc = ConfigParser.SafeConfigParser()
        xmlrpc.read(errata_config_loc)
        self.xmlrpc_url = xmlrpc.get('xmlrpc-info', 'xmlrpc-url')
        self.download_loc = xmlrpc.get('xmlrpc-info', 'download_loc')
        self.mount_base = xmlrpc.get('xmlrpc-info', 'mount_base')

        try:
            self.xmlrpc_url and self.errata_id
        except NameError:
            print "xmlrpc_url or errata_id is not defined"

    def getPackagesURL(self):

        et_rpc_proxy = xmlrpclib.ServerProxy(self.xmlrpc_url)
        response = et_rpc_proxy.getErrataPackages(self.errata_id)

        response = [w.replace(self.mount_base, self.download_loc) for w in response]
        response = set(response)
        return response
