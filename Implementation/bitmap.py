import math
from init import weightRes, Pos, numpy

# bitmap functions

def copyBitmap(bitmapToCopy):

    bitmapRes = len(bitmapToCopy)
    
    bitmap = numpy.empty((bitmapRes, bitmapRes), dtype=type(bitmapToCopy))
    for y in range(bitmapRes):
        for x in range(bitmapRes):
            bitmap[x, y] = bitmapToCopy[x, y]

    return bitmap

def cropBitmap(bitmap):

    bitmapRes = len(bitmap)
    scaleFactor = weightRes / bitmapRes

    croppedBitmap = numpy.full((weightRes, weightRes), 0, dtype=bool)
    corners = [Pos(bitmapRes - 1, bitmapRes - 1), Pos(0, 0)]
    for y in range(bitmapRes):
        for x in range(bitmapRes):
            if bitmap[x, y]:
                
                if x < corners[0].x:
                    corners[0].x = x
                    
                if x > corners[1].x:
                    corners[1].x = x
                    
                if y < corners[0].y:
                    corners[0].y = y
                    
                if y > corners[1].y:
                    corners[1].y = y

    width = corners[1].x - corners[0].x
    height = corners[1].y - corners[0].y
    center = Pos(width / 2 + corners[0].x, height / 2 + corners[0].y)
    xStretchScale = 1
    yStretchScale = 1
    if width >= height:
        frame = width
        yStretchScale = 2 * (center.y - corners[0].y) / frame
        corners[0].y -= (width - height) / 2
    else:
        frame = height
        xStretchScale = 2 * (center.x - corners[0].x) / frame
        corners[0].x -= (height - width) / 2

    multiplier = frame / (bitmapRes - 1)
    for y in range(bitmapRes):
        for x in range(bitmapRes):
            xIndex = int(center.x + (x * multiplier - frame / 2) * xStretchScale)
            yIndex = int(center.y + (y * multiplier - frame / 2) * yStretchScale)
            if xIndex < bitmapRes and yIndex < bitmapRes:
                if bitmap[xIndex, yIndex]:
                    croppedBitmap[int(x * scaleFactor), int(y * scaleFactor)] = True

    return croppedBitmap

def rotateBitmap(bitmap, degrees):

    bitmapRes = len(bitmap)

    flipCount = 0
    while degrees >= 90:
        degrees -= 90
        flipCount += 1
        if flipCount > 3:
            flipCount = 0

    for flip in range(flipCount):
        
        rotatedBitmap = numpy.full((bitmapRes, bitmapRes), False, dtype=bool)
        for y in range(bitmapRes):
            for x in range(bitmapRes):
                if bitmap[x, y]:
                    rotatedBitmap[bitmapRes - y - 1, x] = True

        bitmap = copyBitmap(rotatedBitmap)

    if degrees != 0:

        rotatedRes = int(bitmapRes * math.sqrt(2))
        rotatedBitmap = numpy.full((rotatedRes, rotatedRes), False, dtype=bool)
        center = rotatedRes / 2
        sinAngle = math.sin(math.radians(degrees))
        cosAngle = math.cos(math.radians(degrees))
    
        for y in range(rotatedRes):
            for x in range(rotatedRes):
                xIndex = int((x - center) * cosAngle + (y - center) * sinAngle + bitmapRes / 2)
                yIndex = int((x - center) * -sinAngle + (y - center) * cosAngle + bitmapRes / 2)
                if xIndex in range(bitmapRes) and yIndex in range(bitmapRes) and bitmap[xIndex, yIndex]:
                    rotatedBitmap[x, y] = True

        return rotatedBitmap
    
    else:
        return bitmap

def validateBitmap(bitmap):

    bitmapRes = len(bitmap)

    check = False
    for y in range(bitmapRes):
        for x in range(bitmapRes):
            if not bitmap[x, y]:
                check = True

    return check
