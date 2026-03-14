import math
from random import randint, uniform as randfloat
from init import shapeRes
from bitmap import *

# Random shape generation functions

def randAttributes():

    randomness = randfloat(0, 1)
    center = Pos(randint(int(shapeRes / 3), int(shapeRes * 2 / 3)), randint(int(shapeRes / 3), int(shapeRes * 2 / 3)))
    radius = int((randomness + 1) * shapeRes / 6)
    heightMultiplier = randfloat(0.3, 1)
    widthMultiplier = randfloat(0.3, 1)
    brushSize = int(randfloat(0, 7 * randomness)) + 2

    return randomness, center, radius, heightMultiplier, widthMultiplier, brushSize

def fillShape(bitmap, startPos, volume):

    bitmapRes = len(bitmap)
    bitmapCopy = copyBitmap(bitmap)

    bitmapCopy[startPos.x, startPos.y] = True
    pointsToCheck = [startPos]
    for pos in pointsToCheck:
        if randfloat(0, 1) <= volume:
            bitmap[pos.x, pos.y] = True
            
        if pos.x - 1 >= 0 and not bitmapCopy[pos.x - 1, pos.y]:
            bitmapCopy[pos.x - 1, pos.y] = True
            pointsToCheck.append(Pos(pos.x - 1, pos.y))
            
        if pos.y + 1 < bitmapRes and not bitmapCopy[pos.x, pos.y + 1]:
            bitmapCopy[pos.x, pos.y + 1] = True
            pointsToCheck.append(Pos(pos.x, pos.y + 1))
            
        if pos.x + 1 < bitmapRes and not bitmapCopy[pos.x + 1, pos.y]:
            bitmapCopy[pos.x + 1, pos.y] = True
            pointsToCheck.append(Pos(pos.x + 1, pos.y))
            
        if pos.y - 1 >= 0 and not bitmapCopy[pos.x, pos.y - 1]:
            bitmapCopy[pos.x, pos.y - 1] = True
            pointsToCheck.append(Pos(pos.x, pos.y - 1))

    return bitmap

def drawDot(bitmap, bitmapPos, brushSize, eraser = False):

    bitmapRes = len(bitmap)
    
    for y in range(bitmapPos.y - brushSize, bitmapPos.y + brushSize + 1):
        for x in range(bitmapPos.x - brushSize, bitmapPos.x + brushSize + 1):
            if ((x - bitmapPos.x) ** 2) + ((y - bitmapPos.y) ** 2) - (brushSize ** 2) < 1 and x in range(bitmapRes) and y in range(bitmapRes):
                if not eraser and not bitmap[x, y]:
                    bitmap[x, y] = True
                if eraser and bitmap[x, y]:
                    bitmap[x, y] = False
                
    return bitmap

def drawLine(bitmap, pos1, pos2, brushSize, shapeType, randomness):

    if pos2.x <= pos1.x:
        temp = pos1
        pos1 = pos2
        pos2 = temp

    xDist = (pos1.x - pos2.x)
    yDist = (pos1.y - pos2.y)
    lineLength = math.sqrt(xDist ** 2 + yDist ** 2)
    if xDist != 0:
        angle = math.atan(yDist / xDist)
    else:
        if pos2.y > pos1. y:
            angle = math.pi / 2
        else:
            angle = 3 * math.pi / 2

    xMultiplier = randint(1, 3) * randomness
    xMultiplier2 = randint(3, 5) * randomness
    
    if shapeType == "Hollow_":
        xOffset = randfloat(0, math.tau)
        xOffset2 = randfloat(0, math.tau)
        stepNo = randfloat(lineLength * 0.1, lineLength)
        minBranch = -randomness * lineLength / 20
    else:
        xOffset = math.pi * randint(0, 1)
        xOffset2 = math.pi * randint(0, 1)
        stepNo = lineLength
        minBranch = lineLength / 20

    xOffset3 = randfloat(0, math.pi)
    
    yMultiplier = randfloat(1, 1 + randomness * 2) * randomness
    yMultiplier2 = randfloat(randomness * -3, 0) * randomness

    for step in range(int((randfloat(randfloat(-lineLength / 10, 0), 0) - minBranch) * randomness), int(stepNo + minBranch + randfloat(0, randfloat(0, randomness * lineLength / 10)) * randomness)):
        lineX = step * lineLength / stepNo
        lineDist = lineX / lineLength
        lineY = (yMultiplier * math.sin(xMultiplier * math.pi * lineDist + xOffset) + yMultiplier2 * math.sin(xMultiplier2 * math.pi * lineDist + xOffset2)) * math.sin(math.pi * lineDist + xOffset3)
        bitmapPos = Pos(pos1.x + int((lineX * math.cos(angle)) - (lineY * math.sin(angle))), pos1.y + int((lineX * math.sin(angle)) + (lineY * math.cos(angle))))
        drawDot(bitmap, bitmapPos, brushSize)

    return bitmap

def genCircle(shapeType):

    bitmap = numpy.full((shapeRes, shapeRes), False, dtype=bool)
    randomness, center, radius, heightMultiplier, widthMultiplier, brushSize = randAttributes()

    circumference = math.tau * radius

    xMultiplier = randint(1, 5)
    xMultiplier2 = randint(5, 10)

    if shapeType == "Hollow_":
        xOffset = randfloat(0, math.tau)
        xOffset2 = randfloat(0, math.tau)
        stepNo = randfloat(circumference * 0.05, circumference)
        spiralScale = randfloat(-50, 50) * randomness
        minBranch = -randomness * circumference / 20
    else:
        xOffset = math.pi * randint(0, 1)
        xOffset2 = math.pi * randint(0, 1)
        stepNo = circumference
        spiralScale = 0
        minBranch = circumference / 20
        
    xOffset3 = randfloat(0, math.pi)
    
    yMultiplier = randfloat(1, 1 + randomness * 8) * randomness
    yMultiplier2 = randfloat(randomness * -4, 0) * randomness

    angleOffset = randfloat(0, 1)

    for step in range(int((randfloat(randfloat(-circumference / 10, 0), 0) - minBranch) * randomness), int(stepNo + minBranch + randfloat(0, randfloat(0, randomness * circumference / 10)) * randomness)):
        circleDist = step / stepNo
        circleY = (yMultiplier * math.sin(xMultiplier * math.pi * circleDist + xOffset) + yMultiplier2 * math.sin(xMultiplier2 * math.pi * circleDist + xOffset2)) * math.sin(math.pi * circleDist + xOffset3) + spiralScale * circleDist
        angle = math.tau * (angleOffset - circleDist)
        bitmapPos = Pos(center.x + int(widthMultiplier * math.sin(angle) * (radius - circleY)), center.y + int(heightMultiplier * math.cos(angle) * (radius + circleY)))
        drawDot(bitmap, bitmapPos, brushSize)

    if shapeType == "Partial_":
        fillShape(bitmap, center, randfloat(0.01, 0.1))
    elif shapeType == "Filled_":
        fillShape(bitmap, center, 1)

    return bitmap

def genPolygon(shapeType, cornerNo):

    bitmap = numpy.full((shapeRes, shapeRes), False, dtype=bool)
    randomness, center, radius, heightMultiplier, widthMultiplier, brushSize = randAttributes()

    corners = []
    for loop in range(cornerNo):
        randOffset = randfloat(-randomness / cornerNo, randomness / cornerNo)
        angle = math.tau * ((2 * loop + 1) / (2 * cornerNo)) + randOffset
        corners.append(Pos(center.x + int(widthMultiplier * (radius * math.sin(angle) + randfloat(-1, 1) * randomness * shapeRes / 32)), center.y + int(heightMultiplier * (radius * math.cos(angle) + randfloat(-1, 1) * randomness * shapeRes / 32))))

    for i in range(1, len(corners)):
        drawLine(bitmap, corners[i-1], corners[i], brushSize, shapeType, randomness)
    drawLine(bitmap, corners[0], corners[i], brushSize, shapeType, randomness)

    if shapeType == "Partial_":
        fillShape(bitmap, center, randfloat(0.01, 0.1))
    elif shapeType == "Filled_":
        fillShape(bitmap, center, 1)
        
    return bitmap
