# LIVESTOCK - GRASSHOPPER
LivestockGH is a plugin/library for Grasshopper written in Python.
Currently LivestockGH only works with Rhino5. Make sure that Grasshopper is installed.
GhPython is also needed. It can be downloaded here: http://www.food4rhino.com/app/ghpython

# INSTALLATION
Livestock uses PyMesh to handle geometry.
Currently PyMesh is only available for Linux/Unix, therefore it is necessary to install Bash on your windows machine if you don't have linux server.
#### Install Bash for Windows
An installation guide can be found here: https://msdn.microsoft.com/en-us/commandline/wsl/install_guide
#### Set up SSH connection to Bash
Open Bash and type:
```
sudo apt-get remove openssh-server
sudo apt-get install openssh-server
sudo nano /etc/ssh/sshd_config
```
Set the following:
```
PermitRootLogin no
Port 2222
```
Then add a line beneath it that says: 
```
AllowUsers USER
```
Exchange "USER" with your username for the Linux subsystem
```
PasswordAuthentication yes
UsePrivilegeSeparation no
PubkeyAuthentication no
RSAAuthentication no
```
Save and close sshd_config and the type:
```
sudo service ssh --full-restart
```
#### Install PyMesh
To install PyMesh do the following steps after installing Bash for Windows:
First download and install Anaconda for Linux from https://www.continuum.io/downloads \
Make sure Ubuntu is updated and install some new packages:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 libpython3-dev checkinstall git cmake swig gcc g++ libeigen3-dev libgmp-dev libmpfr-dev libboost-thread-dev libboost-dev
```
Install CGAL-4.10
```
mkdir -p ~/src
cd ~/src
wget https://github.com/CGAL/cgal/releases/download/releases%2FCGAL-4.10/CGAL-4.10.tar.xz
tar xf CGAL-4.10.tar.xz
cd CGAL-4.10
cmake .
make
sudo checkinstall
```
Follow the instructions given by checkinstall. Now download and install PyMesh:
```
cd ~/
git clone https://github.com/qnzhou/PyMesh.git
cd PyMesh/
git submodule init
git submodule update
cd third_party/
mkdir build
cd build/
cmake ..
make -j 2
make install
cd ../../
mkdir build
cd build/
cmake ..
make
make src_tests
make tools
make tools_tests
cd ..
./setup.py install --user
```
To check if everything works run:
```
python -c "import pymesh; pymesh.test()"
```
For PyMesh issues (installation or otherwise) and further information go to: https://github.com/qnzhou/PyMesh

#### Install Anaconda for Windows
As Livestock depends on several non-standard Python libraries, we recommend to install Anaconda to manage the python libraries. We here at Livestock have made an environment where all the python libraries we use are included in.
To download Anaconda go to: https://www.continuum.io/downloads\
At the moment LivestockGH depends on the following python libraries:
- SciPy
- Numpy
- Paramiko

To install Livestock Anaconda Environment:\
Open Windows command promt as administrator and type:
```
conda env create s123455/livestock
```

#### Download Livestock Python Libraries
Open Bash and clone the repositories into the livestock folder with the following command:
```
cd ~/
mkdir livestock
cd livestock/
curl https://codeload.github.com/ocni-dtu/livestock_gh/tar.gz/master | \tar -xz --strip=2 livestock_gh-master/python/classes
curl https://codeload.github.com/ocni-dtu/livestock_gh/tar.gz/master | \tar -xz --strip=2 livestock_gh-master/python/templates
```

#### Grasshopper Components
Download the GH components by cloning the "grasshopper/components" repository and move them to the Grasshopper userObjects folder.
First time you use Livestock you should run the component "Livestock Update".
