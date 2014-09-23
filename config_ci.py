#!/usr/bin/python

import os
import sys
import ConfigParser
import time
import util
from common_ci import ExistingNodes

class SetupConfig():

    def workspace_dir(self):
        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("config/idm_setup.cfg")
        util.log.info (idm_config.sections())

        workspace = os.environ.get('WORKSPACE')
        if not workspace:
            util.log.error("Failed to find WORKSPACE env variable.")
            sys.exit(1)
        else:
            util.log.info("WORKSPACE env variable is %s." % workspace)

        idm_config.set('global', 'workspace', workspace)

        with open('config/idm_setup.cfg', 'wb') as idm_setup_config:
            idm_config.write(idm_setup_config)

    def jenkins_job_name(self):
        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("config/idm_setup.cfg")
        util.log.info (idm_config.sections())
        job_in = os.environ.get('JOB_NAME')
        if not job_in:
            util.log.error("Failed to find JOB_NAME env variable.")
            sys.exit(1)
        else:
            util.log.info("%s is my job." % job_in)

        idm_config.set('global', 'job_name', job_in)

        with open('config/idm_setup.cfg', 'wb') as idm_setup_config:
            idm_config.write(idm_setup_config)


    def identify_nodes(self):
        ipa_config = ConfigParser.SafeConfigParser()
        ipa_config.read("config/ipa_setup.cfg")
        util.log.info (ipa_config.sections())

        resources = ExistingNodes()
        resources.env_check()

        my_nodes = resources.node_check()
        util.log.info (my_nodes)

        ipa_config.set('restraint_xml', 'master', my_nodes[0])

        with open('config/ipa_setup.cfg', 'wb') as ipa_setup_config:
            ipa_config.write(ipa_setup_config)
