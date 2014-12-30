#!/usr/bin/python

import os
from nexus.lib import factory

class Restraint():

    def __init__(self, options, conf_dict):

        self.remove_rpm = conf_dict['restraint']['remove_rpm']
        self.install_rpm = conf_dict['restraint']['install_rpm']

        self.repo = conf_dict['restraint']['rhel4_restraint_repo']

        if options.xml_loc is None:
            self.restraint_xmls = conf_dict['restraint']['xmls']
        else:
            self.restraint_xmls = options.xml_loc

