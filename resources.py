import zipfile, os

TMP_FOLDER = "_tmp"
RESOURCE_FILE = "resources.bin"


class ResourceBrowser:
    def __init__(self, aFilePath):
        self.pZipFile = zipfile.ZipFile(aFilePath)
        os.mkdir(TMP_FOLDER)
    
    def getFile(self, aName):
        return self.pZipFile.open(aName)
    
    def extractFile(self, aName):
        if not os.path.exists("{}/{}".format(TMP_FOLDER, aName)):
            self.pZipFile.extract(aName, TMP_FOLDER)
        return "{}/{}".format(TMP_FOLDER, aName)
   
    def close(self):
        self.pZipFile.close()
        os.rmdir(TMP_FOLDER)


gResourceBrowser = ResourceBrowser(RESOURCE_FILE)

getFile = gResourceBrowser.getFile
extractFile = gResourceBrowser.extractFile
close = gResourceBrowser.close

#print(dir(getFile("Redo.mp3")))
#print(getFile("Redo.mp3").fileno())