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
from subprocess import call
from nexus.lib import logger

class Git():

    def __init__(self, options, conf_dict):
        """
        If no options are provided in CLI then check conf
        """

        if options.project is None:
            self.git_project = conf_dict['git']['git_project']
        else:
            self.git_project = options.project

        logger.log.info("GIT project name: %s" % self.git_project)

        if options.repo is None:
            self.git_repo = conf_dict['git']['git_repo_url']
        else:
            self.git_repo = options.repo
        logger.log.info("GIT repo URL: %s" % self.git_repo)

        if options.branch is None:
            self.git_branch = conf_dict['git']['git_get_branch']
        else:
            self.git_branch = options.branch
        logger.log.info("GIT repo branch: %s" % self.git_branch)

        if options.tar is None:
            self.git_tar = conf_dict['git']['git_tar_out']
        else:
            self.git_tar = options.tar

    def get_archive(self):
        """
        Archive the repository to tar file and extract it.
        """

        if not os.path.exists(self.git_project):
            logger.log.info("Project directory does not exist, creating one")
            os.makedirs(self.git_project)
        git_remote = "--remote=" + self.git_repo
        git_branch = self.git_branch + ":"
        logger.log.info("Archiving git branch...")
        call(["git", "archive", "-v", git_remote, git_branch, "-o", self.git_tar])
        logger.log.info("Extracting the git archive...")
        call(["tar", "-xf", self.git_tar, "-C", self.git_project])
