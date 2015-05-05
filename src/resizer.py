'''
Created on May 5, 2015

@author: Geoff
'''

from PIL import Image
from PIL import ImageFilter
import os

class imgDescr:
    pass

def resizer(f, srcDir, dstDir, size=120):
    srcName = srcDir+f
    img = Image.open(srcName)
    maxDim = max(img.size)
    print img.size, maxDim
    wpercent = (size / float(maxDim))
    vsize = int((float(img.size[0]) * float(wpercent)))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((vsize, hsize), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
    tnName = dstDir+"t_"+f
    img.save(tnName)
    
    tnDesc = imgDescr()
    tnDesc.srcName = srcName
    tnDesc.name = tnName
    tnDesc.width = vsize
    tnDesc.height = hsize
    
    return tnDesc