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
import json
from nexus.lib import logger

class CI_MSG():
    def get_ci_msg_value(self, x):
        self.ci_message = x

        ci_msg = os.environ.get("CI_MESSAGE")
        if ci_msg == "null" or ci_msg is None:
            logger.log.warn("ci_msg not found")
        else:
            data = json.loads(ci_msg)
            logger.log.info(json.dumps(data, indent=4))

            with open('ci_message.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)

            ci_msg_value = data[self.ci_message]
            return ci_msg_value
