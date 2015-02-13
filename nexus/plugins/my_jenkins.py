#!/usr/bin/python

from nexus.lib import logger
import jenkins

class Jenkins():

    def __init__(self, options, conf_dict):

        self.jenkins_master_url = conf_dict['jenkins']['jenkins_master_url']

    def build_job(self, name, conf_dict):
        """build jenkins trigger job"""
        j = jenkins.Jenkins(self.jenkins_master_url)
        trigger_name = conf_dict['triggers'][name]
        j.build_job(trigger_name)
        logger.log.info("Succesfully triggered %s" % trigger_name)

    def main(self, options, conf_dict):
        if options.show_triggers is True:
            triggers = conf_dict['triggers']
            for x in triggers:
                print (x)
        if options.run:
            self.build_job(options.run, conf_dict)
