# Import
import os
import paramiko

# Create output text file
folder = r'C:\livestock\python\templates'
inData = '\\InData.txt'

file_obj = open(folder + inData, 'r')
data = file_obj.readlines()
ip = data[0][:-1]
port = int(data[1][:-1])
user = data[2][:-1]
pw = data[3][:-1]
path = data[4][:-1]
command = data[5]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(ip,port=port,username=user,password=pw)
print('Opening connection')
channel = ssh.invoke_shell()

channel_data = ''

while True:
    if channel.recv_ready():
        channel_bytes = channel.recv(9999)
        channel_data += channel_bytes.decode("utf-8")
        print(channel_data)
    else:
        pass

    if channel_data.endswith('ocni@KONGSGAARD-PC:~$ '):
        channel.send('cd ' + path + '\n')
    elif channel_data.endswith(path[-10:-1] + '$ '):
        channel.send(command + '\n')
    elif os.path.isfile(folder + '\\out.txt'):
        print('Succes!')
        break
    else:
        pass

print('Closing connection!')
os.remove(folder + '\\out.txt')
ssh.close()