
*"Learn to refactor, refactor to learn."*

I understand there are quite a few areas where the above applies, so if you are here 
please feel free to raise an issue with implementation details or pull requests are always welcome.


Nexus - Continuous Integration utility
======================================


* _`Index`:

  * `Manual execution`_:

    - `Installing pre-requisities`_
    - `Cloning repositories`_
    - `Setting environment variables`_
    - `Configuring Nexus`_
    - `Executing manually`_
    - `Adding new test suite`_
  * `CI Workflow`_

Manual execution
================
Installing pre-requisities
==========================
* ssh into the machine where you intend to run Nexus
* Install python-paramiko python-crypto python-BeautifulSoup python-requests python-argparse
* Git clone Nexus and execute "python restraint_repo_finder.py" from nexus/tools

.. code-block:: bash

   tools]# python restraint_repo_finder.py
   ('redhat', '7.0', 'Maipo')
   Downloading http://file.bos.redhat.com/~bpeck/restraint/el7.repo
   <Response [200]>
   Repo file stored in /etc/yum.repos.d/restraint.repo

* yum install restraint-client


Cloning repositories
====================
* Git clone your project repository to, let's say /home/nexus as an example.
* Nexus assumes that you have a restraint directory in your project repository with restraint job xml's
* Git clone Nexus

.. code-block:: bash

    # git clone https://github.com/gsr-shanks/nexus.git
    Cloning into 'nexus'...
    remote: Counting objects: 426, done.
    remote: Compressing objects
    : 100% (5/5), done.
    remote: Total 426 (delta 0), reused 0 (delta 0)Rec
    eiving objects: 100% (426/426), 242.51 KiB | 322.00 KiB/s, done.
    Resolving deltas: 100% (243/243), done.


Setting environment variables
=============================
* export EXISTING_NODES=resource.hostname
* export JOB_NAME=jenkins_job_name (for example, look at etc/ipa.conf)
* export WORKSPACE=location_of_your_test_repo (in this example: /home/nexus)


Configuring Nexus
=================
* Edit etc/global.conf and update your test resource password
* Ensure you have a section in etc/<your-project>.conf which matches value of JOB_NAME
* Ensure you have the restraint xml as specified in you job section of etc/<your-project>.conf in your project automation
* etc/<project-name>.conf:

  1. [JOB_NAME] is called the section, more info https://docs.python.org/2/library/configparser.html
  2. job_name is the name of your restraint xml which by default is expected to be available in project-automation/restraint and can be modified in the global section
  3. type is to identify single-host or multi-host
  4. style is to identify if jenkins is configured for free or matrix project


Executing manually
==================
* python idm_ci.py --project ipa --provisioner beaker

.. code-block:: bash

    # python idm_ci.py
    usage: idm_ci.py [-h] [--async ASYNC] --project PROJECT --provisioner PROVISIONER
    idm_ci.py: error: argument --project is required


Adding new test suite
=====================
* TODO


CI Workflow
===========

.. image:: IdM_CI.png
