# FigurAI - AnArtificial Intelligence Shape Recognition program by Andrew Moffitt
# Generates random shapes, then trains itself using machine learning to figure out what shapes got generated
# Doesn't downscale the shapes when training or testing, so takes longer

import numpy, math, sqlite3 as sql
from random import randint, uniform as randfloat
from datetime import datetime

# Class definitions

class Pos:

    def __init__(this, x, y):

        this.x = x
        this.y = y

class Shape:

    def __init__(this, shapeType, cornerNo):

        this.__shapeType = shapeType
        this.__bitmap = createEmptyBitmap()
        this.__weightmap = readWeights(shapeType)
        this.__cornerNo = cornerNo
        this.needsSave = False

    def getCornerNo(this):

        return this.__cornerNo

    def getBitmap(this):
        
        return this.__bitmap

    def getWeights(this, x = None, y = None):

        if x != None and y != None:
            return this.__weightmap[x, y]
        else:
            return this.__weightmap

    def generate(this):

        shapeCheck = False
        while not shapeCheck:
            
            if this.__shapeType[:6] == "Hollow":
                hollow = True
                shapeType = this.__shapeType[7:]
            else:
                hollow = False
                shapeType = this.__shapeType
            
            if shapeType == "Circle":
                this.__bitmap = genCircle(hollow)
            else:
                this.__bitmap = genPolygon(this.__cornerNo, hollow)

            shapeCheck = checkShape(this.__bitmap)
            if not shapeCheck:
                print("Invalid shape generated!")

    def adjustWeights(this, bitmap, adjustValue):

        for y in range(shapeRes):
            for x in range(shapeRes):
                if bitmap[x, y]:
                    this.__weightmap[x, y] += adjustValue
                    
        this.needsSave = True

# Database functions

def connectToDB():

    conn = None
    try:
        conn = sql.connect(dbFileName)
    except sql.Error as e:
        print(e)
                
    return conn

def readWeights(shape):

    print("\nRetrieving " + shape + " weights from database...")

    weightmap = numpy.empty((shapeRes, shapeRes), dtype=int)
    dbConn = connectToDB()
    if dbConn is not None:
                
        cur = dbConn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " + shape + " (x INT NOT NULL, y INT NOT NULL, weightValue INT NOT NULL);")
        cur.execute("SELECT * FROM " + shape)
        results = cur.fetchall()

        if len(results) == shapeRes ** 2:
            for row in results:
                weightmap[row[0], row[1]] = row[2]
        else:
            print("Error! '" + dbFileName + "' " + shape + " weights are not formatted to " + str(shapeRes) + " x " + str(shapeRes) + "! Resetting weights...")
            cur.execute("DELETE FROM " + shape)
            for y in range(shapeRes):
                for x in range(shapeRes):
                    weightmap[x, y] = 0
                    cur.execute("INSERT INTO " + shape + " VALUES (?, ?, ?)", (x, y, 0))
            dbConn.commit()
                
        cur.close()
        dbConn.close()
        print("Successfully retrieved " + shape + " weights")
            
    else:
        print("Error! Cannot create a connection to '" + dbFileName + "'")

    return weightmap

def updateDB():
        
    dbConn = connectToDB()
    if dbConn is not None:
            
        cur = dbConn.cursor()
        for shape in shapeList:
            if shapes[shape].needsSave:
                print("\nSaving " + shape + " weights...")
                cur.execute("DELETE FROM " + shape)
                for y in range(shapeRes):
                    for x in range(shapeRes):
                        cur.execute("INSERT INTO " + shape + " VALUES (?, ?, ?)", (x, y, int(shapes[shape].getWeights(x, y))))
                shapes[shape].needsSave = False
                print("Successfully saved " + shape + " weights")
                    
        dbConn.commit()
        cur.close()
        dbConn.close()
    
    else:
        print("Error! Cannot create a connection to '" + dbFileName + "'")

# Random shape generation functions

def copyBitmap(bitmapToCopy):
    
    bitmap = numpy.empty((shapeRes, shapeRes), dtype=bool)
    for y in range(shapeRes):
        for x in range(shapeRes):
            bitmap[x, y] = bitmapToCopy[x, y]

    return bitmap

def createEmptyBitmap():
    
    bitmap = numpy.empty((shapeRes, shapeRes), dtype=bool)
    for y in range(shapeRes):
        for x in range(shapeRes):
            bitmap[x, y] = False

    return bitmap

def fillShape(bitmap, startPos):

    bitmap[startPos.x, startPos.y] = True
    pointsToCheck = [startPos]
    for pos in pointsToCheck:
        
        if pos.x - 1 >= 0 and not bitmap[pos.x - 1, pos.y]:
            bitmap[pos.x - 1, pos.y] = True
            pointsToCheck.append(Pos(pos.x - 1, pos.y))
            
        if pos.y + 1 < shapeRes and not bitmap[pos.x, pos.y + 1]:
            bitmap[pos.x, pos.y + 1] = True
            pointsToCheck.append(Pos(pos.x, pos.y + 1))
            
        if pos.x + 1 < shapeRes and not bitmap[pos.x + 1, pos.y]:
            bitmap[pos.x + 1, pos.y] = True
            pointsToCheck.append(Pos(pos.x + 1, pos.y))
            
        if pos.y - 1 >= 0 and not bitmap[pos.x, pos.y - 1]:
            bitmap[pos.x, pos.y - 1] = True
            pointsToCheck.append(Pos(pos.x, pos.y - 1))

    return bitmap

def drawLine(bitmap, pos1, pos2, hollow, brushSize):

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

    randomness = lineLength / shapeRes

    xMultiplier = randint(1, 3)
    xMultiplier2 = randint(3, 5)
    
    if hollow:
        xOffset = randfloat(0, math.tau)
        xOffset2 = randfloat(0, math.tau)
    else:
        xOffset = math.pi * randint(0, 1)
        xOffset2 = math.pi * randint(0, 1)

    xOffset3 = randfloat(0, math.pi)
    
    yMultiplier = randfloat(1, 1 + randomness * 2)
    yMultiplier2 = randfloat(randomness * -3, 0)

    for lineX in range(int(lineLength)):
        lineDist = lineX / lineLength
        lineY = (yMultiplier * math.sin(xMultiplier * math.pi * lineDist + xOffset) + yMultiplier2 * math.sin(xMultiplier2 * math.pi * lineDist + xOffset2)) * math.sin(math.pi * lineDist + xOffset3)
        bitmapPos = Pos(pos1.x + int((lineX * math.cos(angle)) - (lineY * math.sin(angle))), pos1.y + int((lineX * math.sin(angle)) + (lineY * math.cos(angle))))
        drawDot(bitmap, bitmapPos, brushSize)

    return bitmap

def drawDot(bitmap, bitmapPos, brushSize):
    
    for y in range(bitmapPos.y - brushSize, bitmapPos.y + brushSize + 1):
        for x in range(bitmapPos.x - brushSize, bitmapPos.x + brushSize + 1):
            if ((x - bitmapPos.x) ** 2) + ((y - bitmapPos.y) ** 2) - (brushSize ** 2) < 1 and x in range(shapeRes) and y in range(shapeRes):
                bitmap[x, y] = True
                
    return bitmap

def genCircle(hollow):

    bitmap = createEmptyBitmap()

    center = Pos(randint(int(shapeRes / 3), int(shapeRes * 2 / 3)), randint(int(shapeRes / 3), int(shapeRes * 2 / 3)))
    radius = randint(int(shapeRes / 8), int(shapeRes / 2))
    brushSize = randint(2, 8)

    circumference = math.tau * radius

    randomness = 4 * radius / shapeRes

    xMultiplier = randint(1, 5)
    xMultiplier2 = randint(5, 10)

    if hollow:
        xOffset = randfloat(0, math.tau)
        xOffset2 = randfloat(0, math.tau)
    else:
        xOffset = math.pi * randint(0, 1)
        xOffset2 = math.pi * randint(0, 1)
        
    xOffset3 = randfloat(0, math.pi)
    
    yMultiplier = randfloat(1, 1 + randomness * 4)
    yMultiplier2 = randfloat(randomness * -3, 0)

    heightMultiplier = randfloat(0.75, 1)
    widthMultiplier = randfloat(0.75, 1)

    angleOffset = randfloat(0, 1)
    
    for circleX in range(int(circumference)):
        circleDist = circleX / circumference
        circleY = (yMultiplier * math.sin(xMultiplier * math.pi * circleDist + xOffset) + yMultiplier2 * math.sin(xMultiplier2 * math.pi * circleDist + xOffset2)) * math.sin(math.pi * circleDist + xOffset3)
        angle = math.tau * (angleOffset - circleDist)
        bitmapPos = Pos(center.x + int(heightMultiplier * ((radius * math.sin(angle)) - (circleY * math.sin(angle)))), center.y + int(widthMultiplier * ((radius * math.cos(angle)) + (circleY * math.cos(angle)))))

        drawDot(bitmap, bitmapPos, brushSize)

    if not hollow:
        fillShape(bitmap, center)

    return bitmap

def genPolygon(cornerNo, hollow):

    bitmap = createEmptyBitmap()

    corners = []
    randomness = randfloat(0, 1)
    center = Pos(randint(int(shapeRes / 3), int(shapeRes * 2 / 3)), randint(int(shapeRes / 3), int(shapeRes * 2 / 3)))
    radius = int((randomness * 3 + 1) * shapeRes / 8)
    rotation = 1 / (2 * cornerNo)
    #rotation = randfloat(0, 1 / cornerNo)
    for loop in range(cornerNo):
        angle = math.tau * (loop / cornerNo + rotation) + randfloat(-randomness / 5, randomness / 5)
        corners.append(Pos(center.x + int(radius * math.sin(angle) + randfloat(-1, 1) * randomness * shapeRes / 32), center.y + int(radius * math.cos(angle) + randfloat(-1, 1) * randomness * shapeRes / 32)))

    brushSize = randint(2, 8)

    for i in range(1, len(corners)):
        drawLine(bitmap, corners[i-1], corners[i], hollow, brushSize)
    drawLine(bitmap, corners[0], corners[i], hollow, brushSize)

    if not hollow:
        fillShape(bitmap, center)

    return bitmap

def checkShape(bitmap):

    check = False
    for y in range(shapeRes):
        for x in range(shapeRes):
            if not bitmap[x, y]:
                check = True

    return check

# AI functions

def cropBitmap(bitmap):

    bitmapUpscale = numpy.empty((shapeRes, shapeRes), dtype=bool)
    corners = [Pos(shapeRes - 1, shapeRes - 1), Pos(0, 0)]
    for y in range(shapeRes):
        for x in range(shapeRes):
            if bitmap[x, y]:
                
                if x < corners[0].x:
                    corners[0].x = x
                    
                if x > corners[1].x:
                    corners[1].x = x
                    
                if y < corners[0].y:
                    corners[0].y = y
                    
                if y > corners[1].y:
                    corners[1].y = y

            bitmapUpscale[x, y] = False

    width = corners[1].x - corners[0].x
    height = corners[1].y - corners[0].y
    if width >= height:
        frame = width
        diff = int(round((width - height) / 2, 0))
        corners[0].y -= diff
    else:
        frame = height
        diff = int(round((height - width) / 2, 0))
        corners[0].x -= diff
        
    for y in range(shapeRes):
        for x in range(shapeRes):
            xIndex = corners[0].x + int((x * frame) / (shapeRes - 1))
            yIndex = corners[0].y + int((y * frame) / (shapeRes - 1))
            if xIndex < shapeRes and yIndex < shapeRes:
                if bitmap[xIndex, yIndex]:
                    bitmapUpscale[x, y] = True

    return bitmapUpscale

def compareBitmapToWeights(bitmap, shape):

    total = 0
    for y in range(shapeRes):
        for x in range(shapeRes):
            if bitmap[x, y]:
                total += shapes[shape].getWeights(x, y)

    return total

def guessShape(bitmap, possibleShapes):

    totals = {}
    
    for shape in possibleShapes:
        totals[shape] = (compareBitmapToWeights(bitmap, shape), 0)
        for rotationIndex in range(1, 8):
            total = compareBitmapToWeights(rotateBitmap(bitmap, 45 * rotationIndex), shape)
            if total > totals[shape][0]:
                totals[shape] = [total, rotationIndex]

    highestShape = possibleShapes[0]
    for shape in possibleShapes:
        if totals[shape][0] > 0:
            totals[shape][0] = verifyShapeGuess(bitmap, shape, totals[shape][1])
            if totals[shape][0] > totals[highestShape][0]:
                highestShape = shape

    return highestShape

def rotateBitmap(bitmap, degrees):

    rotatedBitmap = createEmptyBitmap()
    center = Pos(shapeRes / 2, shapeRes / 2)
    angleOffset = math.radians(degrees)

    for y in range(shapeRes):
        for x in range(shapeRes):
            
            xDist = (x - center.x)
            yDist = (center.y - y)
            distance = math.sqrt(xDist ** 2 + yDist ** 2)
            
            if yDist != 0:
                angle = math.atan(xDist / yDist)
                if yDist < 0:
                    angle += math.pi
            elif xDist > 0:
                angle = math.pi / 2
            else:
                angle = 3 * math.pi / 2

            pos = Pos(int(center.x + math.sin(angle - angleOffset) * distance), int(center.y - math.cos(angle - angleOffset) * distance))
            if pos.x in range(shapeRes) and pos.y in range(shapeRes):
                rotatedBitmap[x, y] = bitmap[pos.x, pos.y]

    return rotatedBitmap

def verifyShapeGuess(bitmap, shape, startRotation):

    cornerNo = shapes[shape].getCornerNo()
    total = 0
    for rotationIndex in range(cornerNo):
        total += compareBitmapToWeights(rotateBitmap(bitmap, startRotation + rotationIndex * 360 / cornerNo), shape)

    return int(total / cornerNo)

# Main pages

def mainMenu():

    display.fill(darkgrey)
    display.blit(titleFont.render("Figur", 1, white), (290, 60))
    display.blit(titleFont.render("AI", 1, yellow), (660, 60))
    
    pyg.draw.rect(display, white, pyg.Rect((302, 200), (500, 100)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((304, 202), (496, 96)))
    display.blit(bigFont.render("Train AI", 1, white), (465, 215))

    pyg.draw.rect(display, white, pyg.Rect((302, 330), (500, 100)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((304, 332), (496, 96)))
    display.blit(bigFont.render("Test AI", 1, white), (480, 345))

    #pyg.draw.rect(display, white, pyg.Rect((302, 330), (500, 100)))
    #pyg.draw.rect(display, darkgrey, pyg.Rect((304, 332), (496, 96)))
    #display.blit(bigFont.render("Help", 1, white), (500, 345))

    pyg.draw.rect(display, white, pyg.Rect((302, 460), (500, 100)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((304, 462), (496, 96)))
    display.blit(bigFont.render("Quit", 1, white), (505, 475))
        
    pyg.display.flip()

    running = True
    while running:
        
        for event in pyg.event.get():

            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
                # Training mode button
                if event.pos[0] in range(302, 802) and event.pos[1] in range(200, 300):
                    textScreen("Loading...", 445)
                    running = False
                    trainingMode()

                # Testing mode button
                if event.pos[0] in range(302, 802) and event.pos[1] in range(330, 430):
                    textScreen("Loading...", 445)
                    running = False
                    testingMode()

                # Help button
                #if event.pos[0] in range(302, 802) and event.pos[1] in range(330, 430):
                    #textScreen("Loading...", 445)
                    #running = False
                    #helpScreen()

                # Exit button
                if event.pos[0] in range(302, 802) and event.pos[1] in range(460, 560):
                    textScreen("Exiting...", 445)
                    running = False

            # Quit button
            if event.type == pyg.QUIT:
                textScreen("Exiting...", 445)
                running = False

def trainingMode():

    results = []
    
    running = True
    while running:

        if len(results) > 0:
            total = 0
            for result in results:
                total += result
            totalAccuracy = format(total / len(results) * 100, ".2f")
        else:
            totalAccuracy = format(0, ".2f")
        
        if not nogui:
            updateDisplay(totalAccuracy)
        else:
            print()
            print("\nTOTAL ACCURACY: " + str(totalAccuracy) + "%\n(Updated on " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ")")

        for loop in range(updateLoop):
            if running:
                for shapeName in shapeList:

                    possibleShapes = []
                    for shapeCopy in shapeList:
                        possibleShapes.append(shapeCopy)
                    if shapeName[:6] == "Hollow":
                        possibleShapes.remove(shapeName[7:])
                    else:
                        possibleShapes.remove("Hollow_" + shapeName)
                
                    shape = shapes[shapeName]
                    shape.generate()
                    bitmapUpscale = cropBitmap(shape.getBitmap())

                    result = 1
                    for currentShape in possibleShapes:
                        total = compareBitmapToWeights(bitmapUpscale, currentShape)
                        if currentShape == shapeName:
                            if total <= 0:
                                shape.adjustWeights(bitmapUpscale, 1)
                                result -= 1 / (shapeNo - 1)
                        elif total > 0:
                            shapes[currentShape].adjustWeights(bitmapUpscale, -1)
                            result -= 1 / (shapeNo - 1)

                    results.append(result)
                    if len(results) > 10000:
                        del results[0]

                    if not nogui:
                        for event in pyg.event.get():
                            # Main menu button
                            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
                                if event.pos[0] in range(629, 1079) and event.pos[1] in range(565, 640):
                                    textScreen("Saving...", 460)
                                    updateDB()
                                    textScreen("Returning to Main Menu...", 300)
                                    running = False
                                    mainMenu()

                            # Quit button
                            if event.type == pyg.QUIT:
                                textScreen("Saving...", 460)
                                updateDB()
                                textScreen("Exiting...", 445)
                                running = False

        updateDB()

def testingMode():

    def drawBrushButton(brushSize, pos, color):
        pyg.draw.rect(display, color, pyg.Rect(pos, (46, 46)))
        pyg.draw.rect(display, darkgrey, pyg.Rect((pos[0] + 2, pos[1] + 2), (42, 42)))
        for y in range(21):
            for x in range(21):
                if ((x - 10) ** 2) + ((y - 10) ** 2) - (brushSize ** 2) < 1:
                    pyg.draw.rect(display, color, pyg.Rect(((x + 1) * 2 + pos[0], (y + 1) * 2 + pos[1]), (2, 2)))

    def resetBrushButtons():

        drawBrushButton(2, (557, 87), white)
        drawBrushButton(4, (557, 149), white)
        drawBrushButton(6, (557, 212), white)
        drawBrushButton(8, (557, 274), white)

    def setBrushSize(brushSize):

        resetBrushButtons()
        if brushSize == 2:
            drawBrushButton(brushSize, (557, 87), yellow)
        elif brushSize == 4:
            drawBrushButton(brushSize, (557, 149), yellow)
        elif brushSize == 6:
            drawBrushButton(brushSize, (557, 212), yellow)
        elif brushSize == 8:
            drawBrushButton(brushSize, (557, 274), yellow)
        pyg.display.flip()

        return brushSize

    display.fill(darkgrey)

    # Clear screen button
    pyg.draw.rect(display, white, pyg.Rect((25, 565), (450, 75)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((27, 567), (446, 71)))
    display.blit(font.render("Clear Screen", 1, white), (145, 575))

    # Main menu button
    pyg.draw.rect(display, white, pyg.Rect((629, 565), (450, 75)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((631, 567), (446, 71)))
    display.blit(font.render("Return to Main Menu", 1, white), (690, 575))

    # Undo button
    pyg.draw.rect(display, white, pyg.Rect((557, 25), (46, 46)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((559, 27), (42, 42)))

    # Display text
    display.blit(smallFont.render("Draw your own shape in the box", 1, white), (650, 150))
    display.blit(smallFont.render("to the left using the mouse", 1, white), (680, 180))
    display.blit(smallFont.render("FigurAI thinks this shape is a:", 1, white), (675, 300))

    brushSize = setBrushSize(4)

    running = True
    while running:

        pyg.draw.rect(display, darkgrey, pyg.Rect(745, 340, 300, 75))

        # Drawing box
        pyg.draw.rect(display, white, pyg.Rect((25, 25), (516, 516)))
        pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (512, 512)))
        pyg.display.flip()

        bitmap = createEmptyBitmap()
        bitmapBackups = [createEmptyBitmap()]

        mouseDown = False
        clearScreen = False
        while running and not clearScreen:

            mousePos = pyg.mouse.get_pos()
            bitmapPos = Pos(int((mousePos[0] - 27) / 2), int((mousePos[1] - 27) / 2))
            if pyg.mouse.get_pressed()[0] and mousePos[0] in range(27, 539) and mousePos[1] in range(27, 539):
                
                drawDot(bitmap, bitmapPos, brushSize)
                for y in range(bitmapPos.y - brushSize, bitmapPos.y + brushSize + 1):
                    for x in range(bitmapPos.x - brushSize, bitmapPos.x + brushSize + 1):
                        if x in range(shapeRes) and y in range(shapeRes):
                            if bitmap[x, y]:
                                pyg.draw.rect(display, white, pyg.Rect((x * 2) + 27, (y * 2) + 27, 2, 2))
                
                pyg.display.flip()
                mouseDown = True

            elif pyg.mouse.get_pressed()[2] and mousePos[0] in range(27, 539) and mousePos[1] in range(27, 539):

                fillShape(bitmap, bitmapPos)
                pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (512, 512)))
                for y in range(shapeRes):
                    for x in range(shapeRes):
                        if bitmap[x, y]:
                            pyg.draw.rect(display, white, pyg.Rect((x * 2) + 27, (y * 2) + 27, 2, 2))
                pyg.display.flip()
                mouseDown = True
                
            elif mouseDown:

                # Guess the shape after the user releases the mouse button
                bitmapBackups.append(copyBitmap(bitmap))
                
                #shapeGuess = guessShape(cropBitmap(bitmap), shapeList)

                totals = {}
                shapeGuess = shapeList[0]
                for shape in shapeList:
                    totals[shape] = compareBitmapToWeights(cropBitmap(bitmap), shape)
                    if totals[shape] > totals[shapeGuess]:
                        shapeGuess = shape

                #if shapeGuess[:6] == "Hollow":
                #    shapeGuess = shapeGuess[7:]
                        
                pyg.draw.rect(display, darkgrey, pyg.Rect(745, 340, 800, 75))
                display.blit(font.render(shapeGuess + " (" + str(totals[shapeGuess]) + ")", 1, white), (745, 340))
                pyg.display.flip()
                mouseDown = False
            
            for event in pyg.event.get():
                if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:

                    # Clear screen button
                    if event.pos[0] in range(25, 475) and event.pos[1] in range(565, 640):
                        clearScreen = True

                    # Undo button
                    if event.pos[0] in range(557, 602) and event.pos[1] in range(25, 71):
                        if len(bitmapBackups) > 2:
                            bitmap = copyBitmap(bitmapBackups[-2])
                            del bitmapBackups[-2:]
                            pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (512, 512)))
                            for y in range(shapeRes):
                                for x in range(shapeRes):
                                    if bitmap[x, y]:
                                        pyg.draw.rect(display, white, pyg.Rect((x * 2) + 27, (y * 2) + 27, 2, 2))
                            pyg.display.flip()
                            mouseDown = True
                        else:
                            clearScreen = True

                    # Small brush button
                    if event.pos[0] in range(557, 602) and event.pos[1] in range(87, 133):
                        brushSize = setBrushSize(2)

                    # Medium brush button
                    if event.pos[0] in range(557, 602) and event.pos[1] in range(149, 195):
                        brushSize = setBrushSize(4)

                    # Large brush button
                    if event.pos[0] in range(557, 602) and event.pos[1] in range(212, 258):
                        brushSize = setBrushSize(6)

                    # Extra large brush button
                    if event.pos[0] in range(557, 602) and event.pos[1] in range(274, 320):
                        brushSize = setBrushSize(8)

                    # Main Menu button
                    if event.pos[0] in range(629, 1079) and event.pos[1] in range(565, 649):
                        textScreen("Returning to Main Menu...", 300)
                        running = False
                        mainMenu()

                # Quit button
                if event.type == pyg.QUIT:
                    textScreen("Exiting...", 445)
                    running = False

def helpScreen():

    display.fill(darkgrey)

    # Main menu button
    pyg.draw.rect(display, white, pyg.Rect((629, 565), (450, 75)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((631, 567), (446, 71)))
    display.blit(font.render("Return to Main Menu", 1, white), (690, 575))
    pyg.display.flip()

    running = True
    while running:
        for event in pyg.event.get():
            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:

                # Main menu button
                if event.pos[0] in range(629, 1079) and event.pos[1] in range(565, 640):
                    textScreen("Returning to Main Menu...", 300)
                    running = False
                    mainMenu()

            # Quit button
            if event.type == pyg.QUIT:
                textScreen("Exiting...", 445)
                running = False

# Other functions

def findMaxAndMin(weightMap):
    
    max = weightMap[0, 0]
    min = weightMap[0, 0]
    for y in range(1, shapeRes):
        for x in range(1, shapeRes):
            if weightMap[x, y] > max:
                max = weightMap[x, y]
            if weightMap[x, y] < min:
                min = weightMap[x, y]
                
    return max, min

def textScreen(text, xPos):
    
    display.fill(darkgrey)
    display.blit(bigFont.render(text, 1, white), (xPos, 302))
    pyg.display.flip()

def updateDisplay(totalAccuracy): # Needs optimizing
    
    display.fill(darkgrey)
    
    # Display the weight images for each shape
    for i in range(int(shapeNo / 2)):
        
        displayWeights(shapes[shapeList[i * 2]].getWeights(), Pos(i * (shapeRes + 16) + 16, 16))
        displayWeights(shapes[shapeList[i * 2 + 1]].getWeights(), Pos(i * (shapeRes + 16) + 16, 288))

    # Display total accuracy
    display.blit(bigFont.render("Total Accuracy: " + str(totalAccuracy) + "%", 1, white), (64, 565))

    # Main menu button
    pyg.draw.rect(display, white, pyg.Rect((629, 565), (450, 75)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((631, 567), (446, 71)))
    display.blit(font.render("Return to Main Menu", 1, white), (690, 575))

    pyg.display.flip()

def displayWeights(weightMap, offsetPos):

    maximum, minimum = findMaxAndMin(weightMap)
    maxWeight = maximum - minimum
        
    for y in range(shapeRes):
        for x in range(shapeRes):
            brightness = 0
            if (weightMap[x, y] - 1) in range(minimum, maximum):
                brightness += int(((weightMap[x, y] - minimum) / maxWeight) * 255)
            pyg.draw.rect(display, (brightness, brightness, brightness), pyg.Rect(x + offsetPos.x, y + offsetPos.y, 1, 1))



### Main program

print("Launching FigurAI...")

# Program settings
shapeList = ["Circle", "Hollow_Circle", "Triangle", "Hollow_Triangle", "Rectangle", "Hollow_Rectangle", "Pentagon", "Hollow_Pentagon", "Hexagon", "Hollow_Hexagon"]
dbFileName = "assets\database.db"
nogui = False # Runs the program without GUI if True (Disables Pygame)

shapeRes = 256 # Sets the resolution of the weights and of the shapes that get generated
shapeNo = len(shapeList)
updateLoop = 1

shapes = {}
for i in range(shapeNo):
    shape = shapeList[i]
    shapes[shape] = Shape(shape, int(i / 2 + 2))

if nogui:

    trainingMode()

else:

    print()
    import pygame as pyg
    pyg.init()

    windowSize = [1376, 665]
    smallFontSize = 24
    fontSize = 48
    bigFontSize = 64
    titleFontSize = 100
    darkgrey = (  32,   32,   32)
    white = (255, 255, 255)
    yellow = (245, 237, 85)
    
    pyg.display.set_caption("FigurAI")
    display = pyg.display.set_mode(windowSize)
    smallFont = pyg.font.Font("assets\AsapFont.ttf", smallFontSize)
    font = pyg.font.Font("assets\BebasNeueFont.ttf", fontSize)
    bigFont = pyg.font.Font("assets\BebasNeueFont.ttf", bigFontSize)
    titleFont = pyg.font.Font("assets\StretchProFont.otf", titleFontSize)
    
    mainMenu()
    pyg.quit()
