#!/usr/bin/python

from nexus.lib import factory
from nexus.plugins.brew import Brew
from nexus.plugins.git import Git
from nexus.plugins.restraint import Restraint

class CI():

    def __init__(self, options, conf_dict):
        self.provisioner = options.provisioner
        self.builds_from = options.builds_from

    def run(self, options, conf_dict):
        if self.provisioner == "beaker" and self.builds_from == "brew":
            git = Git(options, conf_dict)
            git.get_archive()

            restraint = Restraint(options, conf_dict)
            restraint.run_restraint(options, conf_dict)
            restraint.restraint_junit()
        else:
            print "Unknown provisioner or builds_from"
