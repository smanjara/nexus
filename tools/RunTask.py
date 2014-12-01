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


class SSHClient(paramiko.SSHClient):
    """ This class Inherits paramiko.SSHClient and implements client.exec_commands 
    channel.exec_command """
    
    def __init__(self, hostname=None, port=None, username=None, password=None):
        """ Initialize connection to Remote Host using SSHClient """

        self.hostname = hostname

        if port == None:
            self.port = 22
        else:
            self.port = port
        self.username = username
        self.password = password

        paramiko.SSHClient.__init__(self)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(self.hostname, port=self.port, username=self.username, password=self.password)

    def ExecuteCmd(self, args):
        """ This Function executes commands using SSHClient.exec_commands().
        @params: args: Commands that needs to be executed. Commands which have longer
        outputs or data is buffered should not be excuted using this function. Use ExecuteScript
        function"""
        try:
            stdin, stdout, stderr = self.exec_command(args)
        except paramiko.SSHException, e:
            print "Cannot execute %s", args
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
            sys.exit();
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

def main():

    parser = argparse.ArgumentParser(description="Run Commands on beaker nodes")
    required = parser.add_argument_group('Mandatory Arguments')
    parser.add_argument('--host', help="beaker host",required=True)
    parser.add_argument('--port', type=int, help="SSH Port")
    parser.add_argument('--username', help="Username to connect")
    parser.add_argument('--password', help="User password")
    parser.add_argument('--command', help="Command to Run")
    parser.add_argument('--sourcefile', help="Source file to be copied")
    parser.add_argument('--destfile', help="Destination file name")
    parser.add_argument('--script', help="Script to Run")

    args = parser.parse_args()
    client = SSHClient(args.host, 22, args.username, args.password)

    if args.command:
        stdin, stdout, stderr = client.ExecuteCmd(args.command)
        if stderr:
            for line in stderr.read().splitlines():
                print line
        if stdout:
            for line in stdout.read().splitlines():
                print line
        #Clean up
        stdin.close()
        stdout.close()
        stderr.close()

    if args.script:
        stdout,stderr,exit_status = client.ExecuteScript(args.script)
        output = stdout.getvalue()
        error = stderr.getvalue()
        if error:
            print error
            print exit_status
        else:
            print output

        #clean up
        stdout.close()
        stderr.close()

    if args.sourcefile and args.destfile:
        output = client.CopyFiles(args.sourcefile, args.destfile)
	print output

if __name__ == '__main__':
    main()



