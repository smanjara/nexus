#!/usr/bip/python
# GNU General Public License version 2.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.


import sys
import argparse
import projects.ipa_ci
import projects.rhcs_ci
import common.util


# Parse
parser = argparse.ArgumentParser(description='CI tool')

required = parser.add_argument_group('required arguments')
parser.add_argument('--async', help='build test resources for async')
required.add_argument('--project', help='IdM project name. Accepted values: ipa \
                        ', required=True)
required.add_argument('--provisioner', help='Test resource provisioner. \
                        Accepted values: beaker', required=True)

args = parser.parse_args()
pj = args.project
asy = args.async
pv = args.provisioner

def main():
    if pj == "ipa":
        if pv == "beaker":
            projects.ipa_ci.beaker_run()
        else:
            common.util.log.error("Missing acceptable provisioner name, see help for more info")
    elif pj == "rhcs":
        if pv == "beaker":
            projects.rhcs_ci.beaker_run()
    else:
        common.util.log.error("Missing acceptable project name, see help for more info")

if __name__ == '__main__':
    main()
