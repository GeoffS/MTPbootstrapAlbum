'''
Created on May 4, 2015

@author: gsobering
'''
import sys
import os
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import shutil
from resizer import resizer
import buildLib as bl
from datetime import datetime

scriptVersion = "MTPbootstrapAlbum 1.0"

class struct:
    pass


def readTitle(srcDir):
    titleFilename = srcDir+"title.txt"
    if os.path.exists(titleFilename):
        print "Reading title file: "+titleFilename
        titleFile = open(titleFilename, 'r')
        titleStr = titleFile.readline()
        shortTitleStr = titleFile.readline()
        titleFile.close()
    else:
        titleStr = " "
        shortTitleStr = " "
    return titleStr, shortTitleStr

def createEmptyAlbumDirectory(albumDir, autoClean=True):
    rmTreeOK = struct()
    rmTreeOK.b = False
    def handleErr(func, path, exc_info):
        print "handleErr:", func, path, exc_info
        rmTreeOK.b = (func == os.rmdir)
        print "rmTreeOK=", rmTreeOK.b
    
    if os.path.exists(albumDir):
        if autoClean:
            print "Auto-cleaning "+albumDir
            shutil.rmtree(albumDir, onerror=handleErr)
            if not rmTreeOK.b: return True
        else:
            print "The destination directiory, "+albumDir+", already exists."
            resp = raw_input("Enter 'Y' to delete it, any other key to exit.")
            if resp == 'Y':
                shutil.rmtree(albumDir, onerror=handleErr)
                if not rmTreeOK.b: return True
            else:
                print "Command aborted, no changes made."
                return True
    print albumDir+" cleand."
    if not os.path.exists(albumDir):
        os.makedirs(albumDir)
    return False


def createViewerFile(viewerTemplateFile, tnDescrs, shortAlbumTitle, dstDir):
    destFile = dstDir+'viewer.html' 
    print "\n---------------"
    print viewerTemplateFile+' => '+destFile
    templateTree, templateRoot = bl.loadXmlFileWithIncludes(viewerTemplateFile)
    
    genElem = bl.findElemWith(templateRoot, "meta", "name", "generator")
    genElem.set("content", scriptVersion+" - "+str(datetime.now()))
    
    shortTitleVar = 'var shortAlbumTitle="'+shortAlbumTitle+'";';
    
    imageList = 'var images = ['
    for tn in tnDescrs:
        imageList += "'"+tn.srcBaseName+"',"
    imageList = imageList[:-1]+"]"
    
    hsElem = bl.findElemWithId(templateRoot, "script", "headScript")
    hsElem.text = shortTitleVar + imageList
    
    print "Writing "+destFile
    dest = open(destFile, 'w')
    dest.write(r'<!DOCTYPE html>')
    templateTree.write(dest)
    dest.close()


def createAlbumFile(albumTemplateFile, tnDescrs, dstDir):
    destFile = dstDir+'index.html' 
    print "\n---------------"
    print albumTemplateFile+' => '+destFile
    templateTree, templateRoot = bl.loadXmlFileWithIncludes(albumTemplateFile)
    
    genElem = bl.findElemWith(templateRoot, "meta", "name", "generator")
    genElem.set("content", scriptVersion+" - "+str(datetime.now()))
    
    headerTitleElem = templateRoot.find("head").find("title")
    headerTitleElem.text = albumTitle
     
    titleElem = bl.findElemWithId(templateRoot, "h1", "albumName")
    titleElem.text = albumTitle
    
    photoRow = bl.findDiv(templateRoot, "photoRow")
    
    for tn in reversed(tnDescrs):
        print "Adding "+tn.srcName+" to thumbnail section."
        linkTemplateTree = ElementTree()
        linkTemplateRoot = linkTemplateTree.parse('thumbnail_template.f', parser = bl.CommentedTreeBuilder())
        divElem = linkTemplateRoot.find('div')
        
        aElem = divElem.find('a')
        imgElem = aElem.find('img')
        
        aElem.set('href', 'viewer.html?'+tn.srcBaseName)
        
        imgElem.set('src', tn.baseName)
        width = str(tn.width)
        height = str(tn.height)
        marginTop  = str((imageBkgSize-tn.height)/2)
        marginLeft = str((imageBkgSize-tn.width)/2)
#         imgElem.set('style', 'width:'+width+'px;height:'+height+'px;margin-top:'+marginTop+'px;margin-left:'+marginLeft+'px;')
        imgElem.set('style', 'margin-top:'+marginTop+'px;margin-left:'+marginLeft+'px;')
        imgElem.set('width',  width)
        imgElem.set('height', height)
        
        photoRow.insert(0, divElem)
        
    print "Writing "+destFile
    dest = open(destFile, 'w')
    dest.write(r'<!DOCTYPE html>')
    templateTree.write(dest)
    dest.close()


def createThumbnails(srcDir, dstDir):
    print "Creating thumbnails..."
    tnDescrs = []
    for f in os.listdir(srcDir):
        if f.endswith(".jpg"):
            print "Processing: "+f
            tn = resizer(f, srcDir, dstDir)
            tnDescrs.append(tn)
            shutil.copyfile(srcDir+f, dstDir+f)
    return tnDescrs


def copyFiles(supportFiles, dstDir):
    print "Copying support files..."
    for f in supportFiles:
        shutil.copyfile(f, dstDir+f)
    
    
def addSepIfNecess(f):
    if not f.endswith(os.sep): return f+os.sep
    else:                      return f
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Uasge: srcDir destDir"
        exit()
        
    srcDir = addSepIfNecess(sys.argv[1])
    dstDir = addSepIfNecess(sys.argv[2])

    albumTemplateFile = "albumTemplate.html"
    viewerTemplateFile = 'viewerTemplate.html'
    supportFiles = ["mtp.css", "134GridGrBlu.png", "MTP_Banner_2014_360x40.png", "screenfull.min.js", "spin.min.js", "hammer.min.js", "MTPviewer.js"]
    imageBkgSize = 134 # pixels
    
    print "Create album in '"+dstDir+"' from images in '"+srcDir+"'"
    
    albumTitle, shortAlbumTitle = readTitle(srcDir)
    
    if(createEmptyAlbumDirectory(dstDir)): exit()
        
    copyFiles(supportFiles, dstDir)
    
    tnDescrs = createThumbnails(srcDir, dstDir)

    createAlbumFile(albumTemplateFile, tnDescrs, dstDir)
    
    createViewerFile(viewerTemplateFile, tnDescrs, shortAlbumTitle, dstDir)
    
    print "Done!"