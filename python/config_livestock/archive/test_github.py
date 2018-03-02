url =  'https://github.com/livestock3d/livestock_gh/tree/master/python'

import os
import shutil
import zipfile
import time
import urllib
import System


def downloadSourceAndUnzip():
    """
    Download the source code from github and unzip it in temp folder
    """

    url = "https://github.com/livestock3d/livestock_gh/archive/master.zip""
    targetDirectory = r'C:\livestock'

    # download the zip file
    print("Downloading the source code...")
    zipFile = os.path.join(targetDirectory, os.path.basename(url))

    # if the source file is just downloded then just use the available file
    if os.path.isfile(zipFile) and time.time() - os.stat(zipFile).st_mtime < 1000:
        download = False
    else:
        download = True

        # remove the old version
        try:
            shutil.rmtree(targetDirectory)
        except:
            pass

    # create the target directory
    if not os.path.isdir(targetDirectory): os.mkdir(targetDirectory)

    if download:
        try:
            client = System.Net.WebClient()
            client.DownloadFile(url, zipFile)
            if not os.path.isfile(zipFile):
                print("Download failed! Try to download and unzip the file manually form:\n" + url)
                return
        except Exception, e:
            print(`e` + "\nDownload failed! Try to download and unzip the file manually form:\n" + url)
            return

    # unzip the file
    with zipfile.ZipFile(zipFile) as zf:
        for f in zf.namelist():
            if f.endswith('/'):
                try:
                    os.makedirs(f)
                except:
                    pass
            else:
                zf.extract(f, targetDirectory)

    userObjectsFolder = os.path.join(targetDirectory, r"livestock-master\grasshopper\components")

    return userObjectsFolder


def main(sourceDirectory, updateThisFile, updateAllUObjects):

    if sourceDirectory == None:
        userObjectsFolder = downloadSourceAndUnzip()
        if userObjectsFolder == None: return "Download failed! Read component output for more information!", False
    else:
        userObjectsFolder = sourceDirectory

    destinationDirectory = folders.ClusterFolders[0]

    # copy files from source to destination
    if updateAllUObjects:
        if not userObjectsFolder or not os.path.exists(userObjectsFolder):
            warning = 'source directory address is not a valid address!'
            print
            warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1

        srcFiles = os.listdir(userObjectsFolder)
        # Remove Old version...
        removeCurrentHB()
        print
        'Updating...'
        srcFiles = os.listdir(userObjectsFolder)
        for srcFileName in srcFiles:
            # check for ladybug userObjects
            if srcFileName.StartsWith('Honeybee'):
                srcFullPath = os.path.join(userObjectsFolder, srcFileName)
                dstFullPath = os.path.join(destinationDirectory, srcFileName)

                # check if a newer version is not already exist
                if not os.path.isfile(dstFullPath):
                    shutil.copy2(srcFullPath, dstFullPath)
                # or is older than the new file
                elif os.stat(srcFullPath).st_mtime - os.stat(dstFullPath).st_mtime > 1:
                    shutil.copy2(srcFullPath, dstFullPath)

        # if item selector is not already copied, copy it to component folder
        srcFullPath = os.path.join(userObjectsFolder, "ItemSelector.gha")
        dstFullPath = os.path.join(folders.DefaultAssemblyFolder, "ItemSelector.gha")
        if not os.path.isfile(dstFullPath):
            shutil.copy2(srcFullPath, dstFullPath)

        return "Done!", True

    if updateThisFile:
        # find all the userObjects
        ghComps = getAllTheComponents()

        # for each of them check and see if there is a userObject with the same name is available
        for ghComp in ghComps:
            if ghComp.Name != "Honeybee_Update Honeybee":
                updateTheComponent(ghComp, userObjectsFolder, lb_preparation)

        return "Done!", True


if _updateThisFile or _updateAllUObjects:

    msg, success = main(sourceDirectory_, _updateThisFile, _updateAllUObjects)

    if not success:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    else:
        print
        msg
        try:
            updateLogEXELocation = os.path.join(sc.sticky["Honeybee_DefaultFolder"],
                                                "honeybeeSrc\honeybee-master\UpdateLogs.md")
            textFile = open(updateLogEXELocation, 'r')
            for line in textFile:
                print
                line
        except:
            print
            "There is no update log available now!"
else:
    print
    " "
