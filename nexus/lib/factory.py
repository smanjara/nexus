#!/usr/bin/python

import koji as brew
import threading
import ConfigParser
import json
import urllib2
import os


class Conf_ini(ConfigParser.ConfigParser):
    def conf_to_dict(self):
        """
        Reading a config file into a dictionary.

        In config, you all the items in dictionary, the issue is that you can't
        use it as is. The default data structure is OrderedDict. The k holds the
        section name. The next code creates a dictionary based on _defaults
        OrderedDict(). And for the **d[k], it means that d[k] (dictionary) is
        decomposed into assignments. This is necessary as the dict() method
        requires assignments as additional parameters to the method.
        """
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

class Threader(object):

    def get_item(self, f, item):
        """
        Function which runs a given function in a thread and stores the result.
        """
        result_info = [threading.Event(), None]
        def runit():
            result_info[1] = f(item)
            result_info[0].set()
        threading.Thread(target=runit).start()
        return result_info

    def gather_results(self, result_info):
        """
        Function to gather the results from get_item.
        """
        results = []
        for i in xrange(len(result_info)):
            result_info[i][0].wait()
            results.append(result_info[i][1])
        return results
