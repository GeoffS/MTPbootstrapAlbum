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
        titleFile.close()
    else:
        titleStr = " "
    return titleStr
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Uasge: srcDir destDir"
        exit()
    srcDir = sys.argv[1]
    dstDir = sys.argv[2]

    autoClean = True
    pageTemplateFile = "albumTemplate.html"
    supportFiles = ["mtp.css", "134GridGrBlu.png", "MTP_Banner_2014_360x40.png"]
    imageBkgSize = 134 # pixels
    
    if not srcDir.endswith(os.sep):
        srcDir = srcDir+os.sep
    if not dstDir.endswith(os.sep):
        dstDir = dstDir+os.sep
    
    print "Create album in '"+dstDir+"' from images in '"+srcDir+"'"
    
    albumTitle = readTitle(srcDir)
    
    rmTreeOK = struct()
    rmTreeOK.b = False
    def handleErr(func, path, exc_info):
        print "handleErr:", func, path, exc_info
        rmTreeOK.b = (func == os.rmdir)
        print "rmTreeOK=", rmTreeOK.b
    
    if os.path.exists(dstDir):
        if autoClean:
            print "Auto-cleaning "+dstDir
            shutil.rmtree(dstDir, onerror=handleErr)
            if not rmTreeOK.b:
                exit()
        else:
            print "The destination directiory, "+dstDir+", already exists."
            resp = raw_input("Enter 'Y' to delete it, any other key to exit.")
            if resp == 'y' or resp == 'Y':
                shutil.rmtree(dstDir, onerror=handleErr)
            elif not rmTreeOK.b:
                print "Command aborted, no changes made."
                exit()
    print dstDir+" cleand."
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)
        
    print "Copying support files..."
    for f in supportFiles:
        shutil.copyfile(f, dstDir+f)
    
    print "Creating thumbnails..."
    tnDescrs = []
    for f in os.listdir(srcDir):
        if f.endswith(".jpg"):
            print "Processing: "+f
            tn = resizer(f, srcDir, dstDir)
            tnDescrs.append(tn)
            shutil.copyfile(srcDir+f, dstDir+f)

    destFile = dstDir+'album.html' 
    print "\n---------------"
    print pageTemplateFile+' => '+destFile

    templateTree, templateRoot = bl.loadXmlFileWithIncludes(pageTemplateFile)
    
    genElem = bl.findElemWith(templateRoot, "meta", "name", "generator")
    genElem.set("content", scriptVersion+" - "+str(datetime.now()))
    
    headerTitleElem = templateRoot.find("head").find("title")
    headerTitleElem.text = albumTitle
     
    titleElem = bl.findElemWithId(templateRoot, "h1", "albumName")
    titleElem.text = albumTitle
    
    photoRow = bl.findDiv(templateRoot, "photoRow")
    
#     print "Adding padding lines: ",
#     for i in range(6-(len(tnDescrs) % 6)):
#         divTree, divElem = bl.loadXmlStringWithIncludes(r'<div class="col-xs-6 col-sm-3 col-md-2"> </div>')
#         photoRow.insert(0, divElem)
#         print str(i),
#     print
    
    for tn in tnDescrs:
        print "Adding "+tn.srcName+" to thumbnail section."
        linkTemplateTree = ElementTree()
        linkTemplateRoot = linkTemplateTree.parse('thumbnail_template.f', parser = bl.CommentedTreeBuilder())
        divElem = linkTemplateRoot.find('div')
        
        aElem = divElem.find('a')
        imgElem = aElem.find('img')
        
        aElem.set('href', tn.srcBaseName)
        
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
    
    print "Done!"