#!/usr/bin/env python
""" setup script for nexus """

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='nexus',
    version='1.0',
    description='Nexus - Bridging CI & Automation',
    author='Gowrishankar Rajaiyan',
    author_email='gsr@redhat.com',
    license='GPLv2',
    packages=find_packages(),
    scripts=['bin/nexus'],
    install_requires=[
        'paramiko',
        'ConfigParser',
        'xmlrpclib',
        'simplejson',
        'oslo.config',
        'glob2',
    ],
    include_package_data=True
)
