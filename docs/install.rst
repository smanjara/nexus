Install
=======

* `Build nexus`_:
* `Using RPM`_:

Build nexus
-----------
Installing pre-requisities


- Install the required packages::

    yum install -y \
        git \
        python-setuptools \
        autoconf \
        gcc \
        python-devel \
        tar

    Download and install koji from:
    http://koji.fedoraproject.org/koji/packageinfo?packageID=1181

- Clone nexus git repository::

    git clone https://github.com/gsr-shanks/nexus.git
    cd nexus
    python setup.py install

- Install restraint::

    python nexus/utils/restraint_repo_finder.py
    yum install -y restraint restraint-client


Using RPM
---------
Installing pre-requisities


- Download RPM from::

    https://shanks.fedorapeople.org/nexus/?C=M;O=D
    yum install nexus
