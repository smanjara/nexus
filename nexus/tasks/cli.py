#!/usr/bin/python

import os
import sys
import argparse
from nexus.lib import factory
from nexus.plugins.brew import Brew
from nexus.plugins.errata import Errata

def create_parser():
    parser = argparse.ArgumentParser()
    recursive_parser = argparse.ArgumentParser(add_help=False)

    subparser = parser.add_subparsers(help='brew, errata, restraint or ci',
                                      dest='command')

    parser_brew = subparser.add_parser('brew')
    parser_brew.add_argument('--tag', help='Brew build tag')
    parser_brew.add_argument('--build', help='Brew build name')
    parser_brew.add_argument('--arch', help='Machine arch. Defaults to all if not provided')
    parser_brew.add_argument('--loc', help='Absolute path of download to directory')

    parser_errata = subparser.add_parser('errata')
    parser_errata.add_argument('--release', help='Errata release')
    parser_errata.add_argument('--yaml-loc', help='Errata yaml file location')

    parser_restraint = subparser.add_parser('restraint')
    parser_restraint.add_argument('--repo', help='Restraint repo')
    parser_restraint.add_argument('--xml-loc', help='Restraint xml file location')

    parser_ci = subparser.add_parser('ci')
    parser_ci.add_argument('--provisioner', help='Provisioner for test execution')

    parser.add_argument('--conf', dest='conf', help='configuration file')

    return parser

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = create_parser()
    options = parser.parse_args(argv)
    if not options.command:
        parser.error("Must specify a 'command' to be performed")

    config = setup_conf(options)
    execute(options, config)


def setup_conf(options):

    conf = options.conf
    if os.path.isfile(conf):
        f = factory.Conf_ini()
        f.read(conf)
        conf_dict = f.conf_to_dict()
        return conf_dict

def execute(options, conf_dict):

    if options.command == 'brew':
        brew_1 = Brew(options, conf_dict)
        brew_1.get_latest(options, conf_dict)
    elif options.command == 'errata':
        errata_1 = Errata(options, conf_dict)

if __name__ == '__main__':
    sys.path.insert(0, '.')

