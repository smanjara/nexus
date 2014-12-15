#!/usr/bin/python

import os
import urllib2
import ConfigParser
import xmlrpclib

class Errata():
    """This class is to get values from errata"""

    def __init__(self):
        """Initialize connection to xmlrpc server using xmlrpc_url. errata_id is required
        for initialization, if not given then the script will exit.
        """
        errata_id = os.environ.get("errata_id")
        self.errata_id = errata_id

        workspace_loc = os.environ.get('WORKSPACE')

        errata = ConfigParser.SafeConfigParser()
        ipa_conf_loc = os.path.join(workspace_loc, "nexus/etc/ipa.conf")
        errata.read(ipa_conf_loc)
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

    def dlPackages(self):
        url = self.getPackagesURL()

        for rpm_url in url:
            print rpm_url
            rpm_name = os.path.basename(rpm_url)
            print rpm_name
            u = urllib2.urlopen(rpm_url)
            f = open(rpm_name, 'wb')
            f.write(u.read())
            f.close()
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print("Downloading: {0} Bytes: {1}".format(rpm_url, file_size))
            print(rpm_name)

def main():
    errata = Errata()
    errata.dlPackages()

if __name__ == '__main__':
    main()
