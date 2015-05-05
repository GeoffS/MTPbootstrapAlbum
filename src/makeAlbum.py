'''
Created on May 4, 2015

@author: gsobering
'''
import sys
import os
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
from resizer import resizer
import buildLib as bl

#import buildLib

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Uasge: srcDir destDir"
        exit()
    srcDir = sys.argv[1]
    dstDir = sys.argv[2]
    
    if not srcDir.endswith(os.sep):
        srcDir = srcDir+os.sep
    if not dstDir.endswith(os.sep):
        dstDir = dstDir+os.sep
    
    print "Create album in '"+dstDir+"' from images in '"+srcDir+"'"
    
    pageTemplateFile = "albumTemplate.html"
    
    tnDescrs = []
    for f in os.listdir(srcDir):
        if f.endswith(".jpg"):
            print "Processing: "+f
            tn = resizer(f, srcDir, dstDir)
            tnDescrs.append(tn)
            

    destFile = dstDir+'album.html' 
    print "\n---------------"
    print pageTemplateFile+' => '+destFile
    
    try:
        os.remove(destFile)
    except WindowsError as (errno, strerror):
        #print "WindowsError({0}): {1}".format(errno, strerror)
        #print "Note: No "+destFile+" to remove."
        pass
    

    templateTree, templateRoot = bl.loadXmlFileWithIncludes(pageTemplateFile)
    photoRow = bl.findDiv(templateRoot, "photoRow")
    
    print "Adding padding lines: ",
    for i in range(6-(len(tnDescrs) % 6)):
        divTree, divElem = bl.loadXmlStringWithIncludes(r'<div class="col-xs-6 col-sm-3 col-md-2"> </div>')
        photoRow.insert(0, divElem)
        print str(i),
    print
    
    for tn in tnDescrs:
        print "Adding "+tn.srcName+" to thumbnail section."
        linkTemplateTree = ElementTree()
        linkTemplateRoot = linkTemplateTree.parse('thumbnail_template.f', parser = bl.CommentedTreeBuilder())
        divElem = linkTemplateRoot.find('div')
        
        div2 = divElem.find('div')
        aElem = div2.find('a')
        imgElem = aElem.find('img')
        
        aElem.set('href', tn.srcName)
        
        imgElem.set('src', tn.name)
        imgElem.set('style', 'width:'+str(tn.width)+'px;height:'+str(tn.height)+'px;')
        
        photoRow.insert(0, divElem)
        
    print "Writing "+destFile
    dest = open(destFile, 'w')
    dest.write(r'<!DOCTYPE html>')
    templateTree.write(dest)
    dest.close()
    
    print "Done!"