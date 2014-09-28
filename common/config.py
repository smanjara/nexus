#!/usr/bin/python

import os
import sys
import ConfigParser
import time
import util
from common.nodes import ExistingNodes

class SetupConfig():

    def workspace_dir(self, x):
        self.workspace = x

        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("etc/idm_setup.cfg")
        util.log.info (idm_config.sections())

        workspace = os.environ.get(self.workspace)
        if not workspace:
            util.log.error("Failed to find %s env variable." % self.workspace)
            sys.exit(1)
        else:
            util.log.info("WORKSPACE env variable is %s." % workspace)

        idm_config.set('global', 'workspace', workspace)

        with open('etc/idm_setup.cfg', 'wb') as idm_setup_config:
            idm_config.write(idm_setup_config)

    def jenkins_job_name(self, x):
        self.jobname = x

        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("etc/idm_setup.cfg")
        util.log.info (idm_config.sections())
        job_in = os.environ.get(self.jobname)
        if not job_in:
            util.log.error("Failed to find %s env variable." % self.jobname)
            sys.exit(1)
        else:
            util.log.info("%s is my job." % job_in)

        idm_config.set('global', 'job_name', job_in)

        with open('etc/idm_setup.cfg', 'wb') as idm_setup_config:
            idm_config.write(idm_setup_config)

"""
    def identify_nodes(self):
        ipa_config = ConfigParser.SafeConfigParser()
        ipa_config.read("etc/ipa_setup.cfg")
        util.log.info (ipa_config.sections())

        resources = ExistingNodes()
        resources.env_check()

        my_nodes = resources.node_check()
        util.log.info (my_nodes)

        ipa_config.set('restraint_xml', 'master', my_nodes[0])

        with open('etc/ipa_setup.cfg', 'wb') as ipa_setup_config:
            ipa_config.write(ipa_setup_config)
"""
