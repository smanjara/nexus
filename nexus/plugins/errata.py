#!/usr/bin/python

import os
from nexus.lib import factory

class Errata():

    def __init__(self, options, conf_dict):

        self.errata_xmlrpc = conf_dict['errata']['xmlrpc_url']
        self.errata_download = conf_dict['errata']['download_devel']
        self.errata_mount_base = conf_dict['errata']['mount_base']
        self.errata_rhel64z = conf_dict['errata']['rhel64z']
        self.errata_rhel70z = conf_dict['errata']['rhel70z']

        if options.yaml_loc is None:
            self.errata_yamls = conf_dict['errata']['yamls']
        else:
            self.errata_yamls = options.yaml_loc

