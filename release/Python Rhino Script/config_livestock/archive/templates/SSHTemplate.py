# Import
import os
import paramiko

# Open input text file
localfolder = r'C:\livestock\python\ssh'
inData = '\\InData.txt'

file_obj = open(localfolder + inData, 'r')
data = file_obj.readlines()
file_obj.close()

# Get data
ip = data[0][:-1]
port = int(data[1][:-1])
user = data[2][:-1]
pw = data[3][:-1]
trans = data[4][:-1].split(',')
run = data[5][:-1]


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
sftp.put(localfolder + '/InData.txt', remotefolder + '/InData.txt')

channel = ssh.invoke_shell()

channel_data = ''

com_send = False
folder_send = False
return_send = False
outfile = False

while True:
    # Print shell
    if channel.recv_ready():
        channel_bytes = channel.recv(9999)
        channel_data += channel_bytes.decode("utf-8")
        print(channel_data)

    else:
        pass

    # Execute commands
    if not folder_send:
        sftp.chdir(remotefolder)
        channel.send('cd ' + remotefolder + '\n')
        print('folder send')
        folder_send = True

    elif folder_send and not com_send:
        channel.send('python ' + run + '\n')
        print('command send')
        com_send = True

    else:
        pass

    # Look for outfile
    try:
        outfile = sftp.file(remotefolder + '/out.txt')
    except:
        pass

    if outfile:
        print('Found out file')
        sftp.get(remotefolder + '/out.txt',localfolder + '\\out.txt')
        sftp.remove('out.txt')

    # If found start transfering files and clean up
    if os.path.isfile(localfolder + '\\out.txt'):
        #print('Succes!')

        # Copy result files to local and delete remotely
        print('Copying and deleting result files')

        # Get return files
        sftp.get(remotefolder + '/InData.txt', localfolder + '/InData.txt')
        file_obj = open(localfolder + inData, 'r')
        data = file_obj.readlines()
        file_obj.close()
        ret = data[6].split(',')
        sftp.remove('InData.txt')

        for f in ret:
            print(f)
            sftp.get(remotefolder + '/' + f, localfolder + '/' + f)
            sftp.remove(f)

        # Delete input files
        print('Deleting input files')
        for f in trans:
            #print(f)
            sftp.remove(f)

        break

    else:
        pass

# Remove out file
#os.remove(localfolder + '\\out.txt')

# Close connection
print('Closing connection!')
sftp.close()
ssh.close()