#!/usr/bin/python
# -*- coding: utf-8 -*-
#######################################################################
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
#######################################################################
import paramiko
import argparse
import StringIO
import ConfigParser
import socket
import xmlrpclib
import os

class SSHClient(paramiko.SSHClient):
    """ This class Inherits paramiko.SSHClient and implements client.exec_commands
    channel.exec_command """

    def __init__(self, hostname=None, port=None, username=None, password=None):
        """ Initialize connection to Remote Host using Paramiko SSHClient. Can be
	initialized with hostname, port, username and password.
	if username or passwod is not given, username and password will be taken
	from etc/global.conf.
	"""
        self.hostname = hostname

        if port == None:
            self.port = 22
        else:
            self.port = port
	if username == None or password == None:
		global_config = ConfigParser.SafeConfigParser()
		global_config.read("etc/global.conf")
		self.username = global_config.get('global', 'username')
		self.password = global_config.get('global', 'password')
	else:
		self.username = username
		self.password = password

        paramiko.SSHClient.__init__(self)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
    	    self.connect(self.hostname, port=self.port, username=self.username, password=self.password, timeout=30)
	except (paramiko.AuthenticationException, paramiko.SSHException, socket.error):
	    raise

    def ExecuteCmd(self, args):
        """ This Function executes commands using SSHClient.exec_commands().
        @params: args: Commands that needs to be executed. Commands which have longer
        outputs or data is buffered should not be excuted using this function. Use ExecuteScript
        function"""
        try:
            stdin, stdout, stderr = self.exec_command(args,timeout=30)
        except paramiko.SSHException, e:
            print "Cannot execute %s", args
            raise
        else:
            return stdin, stdout, stderr

    def ExecuteScript(self, args):
        """ This Function Executes commands/scripts using channel.exec_command().
        @params args: Commands/scripts that need to be executed.
        Data received from the command are buffered. """

        transport = self.get_transport()
        stdout = StringIO.StringIO()
        stderr = StringIO.StringIO()
        try:
            channel = transport.open_session()
        except paramiko.SSHException, e:
            print "Session rejected"
            raise
        try:
            channel.exec_command(args)
        except  paramiko.SSHException, e:
            print "Cannot execute %s", args
            channel.close()
        else:
            while not channel.exit_status_ready():
                if channel.recv_ready():
                    data = channel.recv(1024)
                    while data:
                        stdout.write(data)
                        data = channel.recv(1024)
                if channel.recv_stderr_ready():
                    error_buff = channel.recv_stderr(1024)
                    while error_buff:
                        stderr.write(error_buff)
                        error_buff = channel.recv_stderr(1024)

            exit_status = channel.recv_exit_status()

        return stdout,stderr,exit_status

    def CopyFiles(self,source,destination):
	""" This Function copies files to destination nodes
	@param:
	source: name of the file toe be copied
	destination: name of file to be saved at the destination node
	"""
        Transport = self.get_transport()
        sftp = paramiko.SFTPClient.from_transport(Transport)
        FileAttributes = sftp.put(source, destination)
        return FileAttributes

class Errata():
    """This class is to get values from errata"""

    def __init__(self, errata_id):
        """Initialize connection to xmlrpc server using xmlrpc_url. errata_id is required
        for initialization, if not given then the script will exit.
        """
        self.errata_id = errata_id

        idm_config = ConfigParser.SafeConfigParser()
        idm_config.read("etc/global.conf")
        workspace_loc = idm_config.get('global', 'workspace')

        errata = ConfigParser.SafeConfigParser()
        errata.read("etc/ipa.conf")
        errata_config = errata.get('global', 'errata_config')
        errata_config_loc = os.path.join(workspace_loc, errata_config)

        xmlrpc = ConfigParser.SafeConfigParser()
        xmlrpc.read(errata_config_loc)
        self.xmlrpc_url = xmlrpc.get('xmlrpc-info', 'xmlrpc-url')
        self.download_loc = xmlrpc.get('xmlrpc-info', 'download_loc')
        self.mount_base = xmlrpc.get('xmlrpc-info', 'mount_base')

        try:
            self.xmlrpc_url and self.errata_id
        except NameError:
            print "xmlrpc_url or errata_id is not defined"

    def getPackagesURL(self):

        et_rpc_proxy = xmlrpclib.ServerProxy(self.xmlrpc_url)
        response = et_rpc_proxy.getErrataPackages(self.errata_id)

        for rpm in response:
            rpm_url = rpm.replace(self.mount_base, self.download_loc)
            print rpm_url
