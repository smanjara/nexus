#!/usr/bin/python

import os
from subprocess import call

class Git():

    def __init__(self, options, conf_dict):
        """
        If no options are provided in CLI then check conf
        """

        if options.project is None:
            self.git_project = conf_dict['git']['git_project']
        else:
            self.git_project = options.project

        if options.repo is None:
            self.git_repo = conf_dict['git']['git_repo_url']
        else:
            self.git_repo = options.repo

        if options.branch is None:
            self.git_branch = conf_dict['git']['git_get_branch']
        else:
            self.git_branch = options.branch

        if options.tar is None:
            self.git_tar = conf_dict['git']['git_tar_out']
        else:
            self.git_tar = options.tar

    def get_archive(self):
        """
        Archive the repository to tar file and extract it.
        """

        if not os.path.exists(self.git_project):
            os.makedirs(self.git_project)
        git_remote = "--remote=" + self.git_repo
        git_branch = self.git_branch + ":"
        call(["git", "archive", "-v", git_remote, git_branch, "-o", self.git_tar])
        call(["tar", "-xf", self.git_tar, "-C", self.git_project])
