'''
Created on May 4, 2015

@author: gsobering
'''
import sys
import os
import PIL
from PIL import Image
from PIL import ImageFilter

import buildLib

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Uasge: srcDir destDir"
        exit()
    srcDir = sys.argv[1]
    dstDir = sys.argv[2]
    print "Create album in '"+dstDir+"' from images in '"+srcDir+"'"
    
    for f in os.listdir(srcDir):
        if f.endswith(".jpg"):
            print "Processing: "+f
            img = Image.open(srcDir+os.sep+f)
            basewidth = 150
            maxDim = max(img.size)
            print img.size, maxDim
            wpercent = (basewidth / float(maxDim))
            vsize = int((float(img.size[0]) * float(wpercent)))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((vsize, hsize), PIL.Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
            img.save(dstDir+os.sep+"t_"+f)