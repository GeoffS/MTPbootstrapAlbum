'''
Created on May 4, 2015

@author: gsobering
'''
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import os
import struct
import string

doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'

commonSubsitiutions = {'reg':'<sup class="reg">&#174;</sup>', 'sqr':'<sup class="sqr">2</sup>', 'nbsp':'&#160;', 'amp':'&#038;'}

class CommentedTreeBuilder ( ET.XMLTreeBuilder ):
    def __init__ ( self, html = 0, target = None ):
        ET.XMLTreeBuilder.__init__( self, html, target )
        self._parser.CommentHandler = self.handle_comment
    
    def handle_comment ( self, data ):
        self._target.start( ET.Comment, {} )
        self._target.data( data )
        self._target.end( ET.Comment )

def addParent(parent):
    for elem in parent.getchildren():
        elem.parent = parent
        addParent(elem)

def doSubsitutions(fileStr, substitutions, indent=""):
    localSubs = commonSubsitiutions.copy()
    localSubs.update(substitutions)
    print indent+'doSubsitutions:', localSubs
    for key, value in localSubs.items():
        fileStr = string.replace(fileStr, '{'+key+'}', value)
    return fileStr

def loadXmlFileWithIncludes(filename, substitutions={}, indent=""):
    print indent+'loadXmlWithIncludes('+filename+')'
    fileStr = open(filename, 'r').read()
    return loadXmlStringWithIncludes(fileStr, substitutions, indent)

def loadXmlStringWithIncludes(fileStr, substitutions={}, indent=""):
    indent = indent+"   "
    fileStr = doSubsitutions(fileStr, substitutions, indent)
    
    elemTree = ElementTree()
    rootElem = ET.fromstring(fileStr, parser = CommentedTreeBuilder())
    elemTree = ElementTree(rootElem)
    
    addParent(rootElem)
    
    includes = rootElem.iter('gsstinclude')
    for include in includes:
        print indent+"Found include tag:", include.text, include.attrib
        parent = include.parent
        inclTree, inclRoot = loadXmlFileWithIncludes(include.text+'.f', include.attrib, indent)
        i=0
        for elem in parent.getchildren():
            if elem == include: break
            i+=1
        parent.remove(include)
        parent.insert(i, inclRoot[0])
    
    return elemTree, rootElem

def findElemWithId(parentElem, tag, id):
    for elem in list(parentElem):
        if elem.tag == tag:
            idAttrib = elem.get('id')
            if idAttrib != None:
                if idAttrib == id:
                    return elem
        candidateElem = findElemWithId(elem, tag, id)
        if candidateElem != None:
            return candidateElem
    return None

def findDiv(parentElem, idStr):
    for elem in list(parentElem):
        if elem.tag == 'div':
            idAttrib = elem.get('id')
            if idAttrib != None:
                if idAttrib == idStr:
                    return elem
        candidateElem = findDiv(elem, idStr)
        if candidateElem != None:
            return candidateElem
    return None

def findSidebar(parentElem):
    return findDiv(parentElem, 'sidebarLinks')

def addLinkTextTo(elem, linkText):
    if linkText[0] == '&':
        tree, linkRoot = loadXmlStringWithIncludes('<fragment>'+linkText[1:]+'</fragment>', commonSubsitiutions)
        elem.text = linkRoot.text
        for linkElem in linkRoot.getchildren():
            elem.append(linkElem)
    else:
        elem.text = linkText

def insertSidebarLinks(templateRoot, thisFile, links):
    sidebarElem = findSidebar(templateRoot)
    
    reversedLinks = list(links)
    reversedLinks.reverse()
    
    print "reversedLinks:", reversedLinks
    
    for linkTuple in reversedLinks:
        linkText = linkTuple[1]
        file = linkTuple[0]
        linkDest = file+'.html'
        print "Page Link:", file, linkText
    
        if file == "":
            if linkText[0:4] == "raw:":
                print "   Raw HTML file:", linkText[4:]
                linkTemplateTree = ElementTree()
                linkTemplateRoot = linkTemplateTree.parse(linkText[4:], parser = CommentedTreeBuilder())
                separator = True
                pElem = linkTemplateRoot[0]
            else:
                print "   Nav Section: ", linkText
                linkTemplateTree = ElementTree()
                linkTemplateRoot = linkTemplateTree.parse('sidebarSection_template.f', parser = CommentedTreeBuilder())
                separator = True
                pElem = linkTemplateRoot.find('p')
                spanElem = pElem.find('span')
                #spanElem.text=linkText
                addLinkTextTo(spanElem, linkText)
        elif linkText[0] == ">" or linkText[0] == "*":
            print "   Nav Indent:",
            if file == thisFile:
                print " No Link:", linkText[1:]
                linkTemplateTree = ElementTree()
                linkTemplateRoot = linkTemplateTree.parse('sidebarIndentNoLink_template.f', parser = CommentedTreeBuilder())
                separator = False
                pElem = linkTemplateRoot.find('p')
                spanElem = pElem.find('span')
                #spanElem.text=linkText[1:]
                addLinkTextTo(spanElem, linkText[1:])
            else:
                print " Link:", linkText[1:], linkDest
                linkTemplateTree = ElementTree()
                linkTemplateRoot = linkTemplateTree.parse('sidebarIndentLink_template.f', parser = CommentedTreeBuilder())
                separator = False
                pElem = linkTemplateRoot.find('p')
                aElem = pElem.find('a')
                #aElem.text=linkText[1:]
                addLinkTextTo(aElem, linkText[1:])
                aElem.set('href', linkDest)
            if linkText[0] == "*":
                pElem.attrib['style']='margin-top:5px;'
                print "   +margin-top:5px;"
            else:
                print
        else:
            print "   Nav", 
            if file == thisFile:
                print "No Link:", linkText
                linkTemplateTree = ElementTree()
                linkTemplateRoot = linkTemplateTree.parse('sidebarNoLink_template.f', parser = CommentedTreeBuilder())
                separator = True
                pElem = linkTemplateRoot.find('p')
                spanElem = pElem.find('span')
                #spanElem.text=linkText
                addLinkTextTo(spanElem, linkText)
            else:
                print "   Link:", linkText, linkDest
                linkTemplateTree = ElementTree()
                linkTemplateRoot = linkTemplateTree.parse('sidebarLink_template.f', parser = CommentedTreeBuilder())
                separator = True
                pElem = linkTemplateRoot.find('p')
                aElem = pElem.find('a')
                #aElem.text=linkText
                addLinkTextTo(aElem, linkText)
                aElem.set('href', linkDest)
            
        sidebarElem.insert(0, pElem)
        if separator and linkText != "Home":
            print "Adding separator"
            sidebarElem.insert(0, ET.fromstring("<hr />"))


# Adaoted from: 
#   http://markasread.net/post/17551554979/get-image-size-info-using-pure-python-code
def jpgDims(jpegFile):
    jpeg = open(jpegFile, 'rb')
    jpeg.read(2)
    b = jpeg.read(1)
    try:
        while (b and ord(b) != 0xDA):
            while (ord(b) != 0xFF): b = jpeg.read
            while (ord(b) == 0xFF): b = jpeg.read(1)
            if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                jpeg.read(3)
                h, w = struct.unpack(">HH", jpeg.read(4))
                break
            else:
                jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
            b = jpeg.read(1)
        width = int(w)
        height = int(h)
    except struct.error:
        pass
    except ValueError:
        pass
 
    return width, height


def standard(srcRoot):
    return srcRoot.getchildren()

photoNavDivWidth = 762
photoNavLineWidth = 740
photoNavImgWidth = 100 + 2*(2+1)

def photoNav(srcRoot):
    for imagesElem in srcRoot.iter('images'):
        images = [e.text for e in imagesElem.findall('image')]
        print "Images:", images
        
        srcRoot.remove(imagesElem)
        
    imageNav = findElemWithId(srcRoot, 'div', 'navImages')
    imageList = findElemWithId(srcRoot, 'div', 'imageList')
    i = 1
    lineWidth = 0
    navLine = ET.SubElement(imageNav, 'div')
    for image in images:
        #'<a href="#'+str(i)+'"><img src="'+image+'_100.jpg" height="100" width="100" /></a>')
        #'<a id="'+str(i)+'1"><div class="img650"><img src="'+image+'_650.jpg" width="650" height="650" /></div></a>')
        if lineWidth+photoNavImgWidth > photoNavLineWidth or image=='br':
            navLine.set('style', 'margin-left:'+str((photoNavDivWidth-lineWidth)/2)+'px; margin-right:auto;')
            lineWidth = 0
            navLine = ET.SubElement(imageNav, 'div')
        
        if image != 'br':    
            navA = ET.SubElement(navLine, 'a', {'href':'#'+str(i)})
            if image.find('%') == -1:
                img100 = image+'_100.jpg'
                img650 = image+'_650.jpg'
            else:
                img100 = image.replace('%', '100')+'.jpg'
                img650 = image.replace('%', '650')+'.jpg'
                
            ET.SubElement(navA, 'img', {'src':img100, 'height':'100', 'width':'100'})
            
            aList = ET.SubElement(imageList, 'a', {'id':str(i)})
            divList = ET.SubElement(aList, 'div', {'class':'img650'})
             
            (width, height) = jpgDims(topDestDir+img650)
            ET.SubElement(divList, 'img', {'src':img650, 'height':str(height), 'width':str(width)})
             
            lineWidth+=photoNavImgWidth
            i+=1
    if lineWidth != 0: 
        navLine.set('style', 'margin-left:'+str((photoNavDivWidth-lineWidth)/2)+'px; margin-right:auto;')
    
    return srcRoot.getchildren()
