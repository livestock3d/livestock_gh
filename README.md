# LIVESTOCK - GRASSHOPPER
LivestockGH is a plugin/library for Grasshopper written in Python

# INSTALLATION
Livestock uses PyMesh to handle geometry.
Currently PyMesh is only available for Linux/Unix, therefore it is neacesary to install Bash on your windows machine if you don't have linux server.
An installation guide can be found here: https://msdn.microsoft.com/en-us/commandline/wsl/install_guide

To install PyMesh go to: https://github.com/qnzhou/PyMesh and follow the instructions. 
Please note that the current CGAL which comes with PyMesh is not new enough to run PyMesh. Therefore follow the instructions given here: https://askubuntu.com/questions/668438/install-cgal-lib-version-4-5-1 and replace the version with the newest version which can be found here: https://github.com/CGAL/cgal/releases

As PyMesh depends on both having Numpy and SciPy installed, we recormend to install Anaconda to manage the python libraries. We here at Livestock have made an environment where all the python libraries we use are included in.
To download Anaconda go to: https://www.continuum.io/DOWNLOADS
To download Livestock Anaconda Environment go to: ---
At the moment LivestockGH depends on the following python libraries:
- SciPy
- Numpy
- Paramiko

Clone the repositories into the livestock folder with the following command:
```
cd /home/<"user">
mkdir livestock
cd livestock
curl https://codeload.github.com/livestock3d/livestock_gh/tar.gz/master | \tar -xz --strip=2 livestock_gh-master/python/classes
curl https://codeload.github.com/livestock3d/livestock_gh/tar.gz/master | \tar -xz --strip=2 livestock_gh-master/python/templates
```

# Windows
Download the GH components by cloning the "grasshopper/components" repository and move them to the Grasshopper userObjects folder.
First time you use Livestock you should run the component "Livestock Update".
