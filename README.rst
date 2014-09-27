
*"Learn to refactor, refactor to learn."*

I understand there are quite a few areas where the above applies, so if you are here 
please feel free to raise an issue with implementation details or pull requests are always welcome.


Continuous Integration utilities
================================


* pre-requisite for manual execution

1. export EXISTING_NODES=resource.hostname 
2. export JOB_NAME=jenkins_job_name 
3. export WORKSPACE=location_of_your_test_repo 

Usage example: python idm_ci.py --project ipa --provisioner beaker

.. code-block:: bash

    # python idm_ci.py 
    usage: idm_ci.py [-h] [--async ASYNC] --project PROJECT --provisioner PROVISIONER
    idm_ci.py: error: argument --project is required

