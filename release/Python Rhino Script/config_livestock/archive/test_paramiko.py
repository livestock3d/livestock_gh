from paramiko import client

class ssh:
    client = None

    def __init__(self, address, port, username, password):
        # Let the user know we're connecting to the server
        print("Connecting to server.")
        # Create a new SSH client
        self.client = client.SSHClient()
        # The following line is required if you want the script to be able to access a server that's not yet in the known_hosts file
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        # Make the connection
        self.client.connect(address,port=port, username=username, password=password, look_for_keys=False)

    def sendCommand(self, command):
        # Check if connection is made previously
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print stdout data when available
                if stdout.channel.recv_ready():
                    # Retrieve the first 1024 bytes
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        # Retrieve the next 1024 bytes
                        alldata += stdout.channel.recv(1024)

                    # Print as string with utf8 encoding
                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")


connection = ssh("127.0.0.1", 2222,"ocni","4320lejre")
connection.sendCommand("cd /mnt/c/Users/Christian/Desktop && mkdir test")

"""

import threading, paramiko, sys

class ssh:
    shell = None
    client = None
    transport = None

    def __init__(self, address, port, username, password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, port=port, username=username, password=password, look_for_keys=False)
        self.transport = paramiko.Transport((address, port))
        self.transport.connect(username=username, password=password)

        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()

    def closeConnection(self):
        if (self.client != None):
            self.client.close()
            self.transport.close()

    def openShell(self):
        self.shell = self.client.invoke_shell()

    def sendShell(self, command):
        if (self.shell):
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")

    def process(self):
        global connection
        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                print(strdata, end="")
                if (strdata.endswith("$ ")):
                    print("\n$ ", end="")


sshUsername = "ocni"
sshPort = 2222
sshPassword = "4320lejre"
sshServer = "127.0.0.1"

connection = ssh(sshServer, sshPort, sshUsername, sshPassword)
connection.openShell()
while True:
    command = input('$ ')
    if command.startswith(" "):
        command = command[1:]
    connection.sendShell(command)
"""