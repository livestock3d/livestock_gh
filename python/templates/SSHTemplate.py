# Import
import os
import paramiko

# Open input text file
localfolder = r'C:\livestock\python\ssh'
inData = '\\InData.txt'

file_obj = open(localfolder + inData, 'r')
data = file_obj.readlines()

# Get data
ip = data[0][:-1]
port = int(data[1][:-1])
user = data[2][:-1]
pw = data[3][:-1]
trans = data[4][:-1].split(',')
run = data[5][:-1]
ret = data[6].split(',')

remotefolder = '/home/' + user + '/livestock/templates'


# Start SSH session
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(ip,port=port,username=user,password=pw)
print('Opening connection')

# Copy files to remove server
sftp = ssh.open_sftp()
for f in trans:
    sftp.put(localfolder + '/' + f, remotefolder + '/' + f)

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
        channel.send('cd ' + remotefolder + '\n')

    elif channel_data.endswith(remotefolder[-10:-1] + '$ '):
        channel.send('python ' + run + '\n')

    try:
        sftp.get(remotefolder + '/out.txt', localfolder + '/out.txt')
    except:
        pass

    elif os.path.isfile(localfolder + '\\out.txt'):
        print('Succes!')

        # Copy result files to local and delete remotely
        for f in ret:
            sftp.get(remotefolder + '/' + f)
            channel.send('rm ' + remotefolder + '/' + f)

        # Delete input files
        for f in trans:
            channel.send('rm ' + remotefolder + '/' + f)

        break

    else:
        pass

# Remove out file
os.remove(localfolder + '\\out.txt')

# Close connection
print('Closing connection!')
sftp.close()
ssh.close()