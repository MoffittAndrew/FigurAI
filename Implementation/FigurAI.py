# FigurAI - An Artificial Intelligence Shape Recognition program by Andrew Moffitt
# Generates random shapes, then trains itself using machine learning to figure out what shapes got generated

from datetime import datetime
from init import *
from bitmap import *
from dbConn import *
from shapeGen import *

class Shape:

    def __init__(this, shapeName, shapeType, cornerNo):

        this.__shapeName = shapeName
        this.__shapeType = shapeType
        this.__cornerNo = cornerNo
        this.__bitmap = numpy.full((shapeRes, shapeRes), False, dtype=type)
        this.__weightmap = numpy.full((weightRes, weightRes), 0, dtype=int)
        this.__needsSave = False

    def getBitmap(this):
        
        return this.__bitmap

    def getWeights(this):

        return this.__weightmap

    def getNeedsSave(this):

        return this.__needsSave

    def setWeights(this, weightmap):

        this.__weightmap = weightmap

    def generate(this):

        shapeCheck = False
        while not shapeCheck:
            
            if this.__shapeName == "Circle":
                bitmap = genCircle(this.__shapeType)
            else:
                bitmap = genPolygon(this.__shapeType, this.__cornerNo)

            shapeCheck = validateBitmap(bitmap)
            if not shapeCheck:
                print("Invalid shape generated! Regenerating new shape...")

        this.__bitmap = bitmap

    def adjustWeights(this, bitmap, adjustValue):

        for y in range(weightRes):
            for x in range(weightRes):
                if bitmap[x, y]:
                    this.__weightmap[x, y] += adjustValue
                    
        this.__needsSave = True

    def saveWeights(this):

        updateDB(this.__shapeType + this.__shapeName, this.__weightmap)
        this.__needsSave = False

# AI functions

def compareBitmapToWeights(bitmap, weightmap):

    total = 0
    for y in range(weightRes):
        for x in range(weightRes):
            if bitmap[x, y]:
                total += weightmap[x, y]

    return total

def guessShape(bitmap, buttons):

    croppedBitmap = cropBitmap(bitmap)

    bitmaps = []
    rotationSteps = int(globalSettings.getRotationSteps() / 4)
    progress = 0
    highestTotals = {}
    for shapeName in shapeList:
        highestTotals[shapeName] = 0

    finalRotation = False
    analyzing = True
    for rotationIndex in range(4):
        for rotation in range(rotationSteps):
            if analyzing:

                if rotationIndex == 0:
                    processedBitmap = cropBitmap(rotateBitmap(croppedBitmap, rotation * (90 / rotationSteps)))
                    bitmaps.append(processedBitmap)
                else:
                    processedBitmap = rotateBitmap(bitmaps[rotation], 90 * rotationIndex)

                for shapeName in shapeList:
                    
                    mixedTotal = 0
                    for shapeType in shapeTypes:
                        total = compareBitmapToWeights(processedBitmap, shapes[shapeType + shapeName].getWeights())
                        if total > 0:
                            mixedTotal += total
                
                    if mixedTotal > highestTotals[shapeName]:
                        highestTotals[shapeName] = mixedTotal

                displayBitmap(processedBitmap, Pos(620, 27))
                progress += 1 / (4 * rotationSteps)
                
                pyg.draw.rect(display, darkgrey, pyg.Rect((701, 58), (300, 30)))
                display.blit(smallFont.render("Analyzing shape... (" + format(progress * 100, ".0f") + "%)", 1, white), (701, 58))
                
                pyg.draw.rect(display, green, pyg.Rect((703, 27), (round(progress * 364, 0), 20)))

                if rotationIndex == 3 and rotation == rotationSteps - 1:
                    finalRotation = True
                displayResults(highestTotals, finalRotation)

                action, running = detectAction(buttons)
                if action != "":
                    analyzing = False
    
    return action, running

# Main pages

def mainMenu():

    display.fill(darkgrey)
    display.blit(titleFont.render("Figur", 1, white), (285, 60))
    display.blit(titleFont.render("AI", 1, yellow), (655, 60))
    buttons = [
        TextButton(Pos(132, 200), (400, 100), "exit_train", "Train AI", bigFont),
        TextButton(Pos(562, 200), (400, 100), "exit_test", "Test AI", bigFont),
        TextButton(Pos(132, 330), (400, 100), "exit_info", "Info", bigFont),
        TextButton(Pos(562, 330), (400, 100), "exit_settings", "Settings", bigFont),
        TextButton(Pos(347, 460), (400, 100), "exit", "Quit", bigFont)
    ]

    running = True
    while running:
        action, running = detectAction(buttons)
            
    if action == "train":
        textScreen("Loading...")
        trainingMode()
    elif action == "test":
        textScreen("Loading...")
        testingMode()
    elif action == "info":
        helpScreen()
    elif action == "settings":
        settings()

def trainingMode():

    display.fill(darkgrey)
    buttons = [
        TextButton(Pos(619, 566), (450, 80), "exit_menu", "Return to Main Menu", font)
    ]

    results = {}
    for i in range(len(shapeList)):
        shapeName = shapeList[i]
        results[shapeName] = []
        textRect = smallFont.render(shapeName, 1, white)
        display.blit(textRect, textRect.get_rect(center = (i * 143 + 124, 40)))
        for i2 in range(len(shapeTypes)):
            if i == 0:
                textRect = pyg.transform.rotate(smallFont.render(shapeTypes[i2][:-1], 1, white), 90)
                display.blit(textRect, textRect.get_rect(center = (40, i2 * 143 + 124)))
            displayWeights(shapes[shapeTypes[i2] + shapeName].getWeights(), Pos(i * 143 + 60, i2 * 143 + 60))

    pyg.draw.rect(display, white, pyg.Rect((797, 60), (260, 260)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((799, 62), (256, 256)))
    randShapeName = ""
    randShapeType = ""
    randBitmap = numpy.full((shapeRes, shapeRes), False, dtype=bool)
    
    running = True
    while running:

        for loop in range(globalSettings.getsaveInterval()):

            pyg.draw.rect(display, darkgrey, pyg.Rect((799, 0), (260, 60)))
            textRect = smallFont.render(randShapeType[:-1] + " " + randShapeName, 1, white)
            display.blit(textRect, textRect.get_rect(center = (927, 40)))
            displayBitmap(randBitmap, Pos(799, 62))

            randShapeName = shapeList[randint(0, len(shapeList) - 1)]
            randShapeType = shapeTypes[randint(0, len(shapeTypes) - 1)]

            accuracies = []
            totalAccuracy = 0
            for shapeName2 in shapeList:
                accuracy = calcAccuracy(results[shapeName2])
                totalAccuracy += accuracy
                accuracies.append((shapeName2, accuracy))

            accuracies = insertionSort(accuracies)
            accuracies.append(("TOTAL ACCURACY", totalAccuracy / len(accuracies)))
            pyg.draw.rect(display, darkgrey, pyg.Rect((775, 340), (300, 200)))
            for i in range(len(accuracies)):
                yOffset = 340
                if i == len(accuracies) - 1:
                    yOffset += 20
                display.blit(smallFont.render(accuracies[i][0] + ": " + format(accuracies[i][1], ".2f") + "%", 1, white), (780, i * 30 + yOffset))

            for shapeName in shapeList:
                for shapeType in shapeTypes:
                    if running:
                    
                        shape = shapes[shapeType + shapeName]
                        shape.generate()
                        croppedBitmap = cropBitmap(shape.getBitmap())
                        rotatedBitmap = cropBitmap(rotateBitmap(croppedBitmap, randint(0, 360)))

                        if shapeName == randShapeName and shapeType == randShapeType:
                            randBitmap = copyBitmap(shape.getBitmap())

                        if compareBitmapToWeights(croppedBitmap, shape.getWeights()) <= 0:
                            shape.adjustWeights(croppedBitmap, 1)
                            results[shapeName].append(False)
                        else:
                            results[shapeName].append(True)

                        if len(results[shapeName]) > 10000:
                            del results[shapeName][0]

                        for otherShapeName in shapeList:
                            if otherShapeName != shapeName:
                                for otherShapeType in shapeTypes:
                                    if compareBitmapToWeights(rotatedBitmap, shapes[otherShapeType + otherShapeName].getWeights()) > 0:
                                        shapes[otherShapeType + otherShapeName].adjustWeights(rotatedBitmap, -1)
                                        results[otherShapeName].append(False)
                                    else:
                                        results[otherShapeName].append(True)

                                    if len(results[otherShapeName]) > 10000:
                                        del results[otherShapeName][0]

                        action, running = detectAction(buttons)

                        if action == "menu":
                            textScreen("Saving...")

        # Save and display the weight images for each shape

        if running:
            pyg.draw.rect(display, darkgrey, pyg.Rect((160, 500), (300, 100)))
            textRect = bigFont.render("Saving...", 1, white)
            display.blit(textRect, textRect.get_rect(center = (310, 550)))
            pyg.display.flip()
        
        for i in range(len(shapeList)):
            for i2 in range(len(shapeTypes)):
                shapeID = shapeTypes[i2] + shapeList[i]
                if shapes[shapeID].getNeedsSave():
                    displayWeights(shapes[shapeID].getWeights(), Pos(i * 143 + 60, i2 * 143 + 60))
                    shapes[shapeID].saveWeights()

        pyg.draw.rect(display, darkgrey, pyg.Rect((10, 500), (600, 170)))
        textRect = bigFont.render("Saved", 1, white)
        display.blit(textRect, textRect.get_rect(center = (310, 550)))
        textRect = font.render("Last saved at " + datetime.now().strftime("%H:%M:%S"), 1, white)
        display.blit(textRect, textRect.get_rect(center = (310, 620)))

    if action == "menu":
        mainMenu()
        
def testingMode():

    display.fill(darkgrey)
    buttons = [
        TextButton(Pos(619, 566), (450, 80), "exit_menu", "Return to Main Menu", font),
        BrushButton(Pos(557, 25), (46, 46), "undo"),
        BrushButton(Pos(557, 87), (46, 46), "brush_8"),
        BrushButton(Pos(557, 149), (46, 46), "brush_12"),
        BrushButton(Pos(557, 212), (46, 46), "brush_16"),
        BrushButton(Pos(557, 274), (46, 46), "brush_eraser"),
        BrushButton(Pos(557, 334), (46, 46), "brush_fill")
    ]
    
    clearButton = TextButton(Pos(25, 566), (245, 80), "clear", "Clear Screen", font)
    submitButton = TextButton(Pos(296, 566), (245, 80), "submit", "Submit", font)

    brush = 12
    buttons[3].setPermColor(yellow)
    bitmapSize = 512

    # Drawing box outline
    pyg.draw.rect(display, white, pyg.Rect((25, 25), (bitmapSize + 4, bitmapSize + 4)))

    # Progress bar outline
    pyg.draw.rect(display, white, pyg.Rect((701, 25), (368, 24)))

    # Mini shape display outline
    pyg.draw.rect(display, white, pyg.Rect((618, 25), (68, 68)))

    running = True
    while running:

        # Reset drawing box
        pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (bitmapSize, bitmapSize)))

        # Show display text
        textRect = smallFont.render("Test the AI by drawing a shape here", 1, white)
        display.blit(textRect, textRect.get_rect(center = (283, 283)))
        emptyBitmap = True
        
        # Hide the "Analyzing..." text
        pyg.draw.rect(display, darkgrey, pyg.Rect((701, 58), (300, 30)))

        # Reset mini shape display
        pyg.draw.rect(display, darkgrey, pyg.Rect((620, 27), (64, 64)))

        # Reset progress bar
        pyg.draw.rect(display, darkgrey, pyg.Rect((703, 27), (364, 20)))

        # Reset shape guesses
        pyg.draw.rect(display, darkgrey, pyg.Rect((618, 108), (476, 558)))
        
        # Reset "Clear Screen" and "Submit" buttons
        buttons = buttons[:7]
        clearButton.setColor(lightgrey)
        submitButton.setColor(lightgrey)

        # Reset the bitmap and the bitmap history
        bitmap = numpy.full((bitmapSize, bitmapSize), False, dtype=bool)
        bitmapBackups = []
        
        mouseDown = False
        fillDown = False
        clearScreen = False
        while running and not clearScreen:

            mousePos = pyg.mouse.get_pos()
            if pyg.mouse.get_pressed()[0] and mousePos[0] in range(27, bitmapSize + 27) and mousePos[1] in range(27, bitmapSize + 27):

                if emptyBitmap and brush != "eraser":
                    pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (bitmapSize, bitmapSize)))
                    emptyBitmap = False

                mouseDown = True
                bitmapPos = Pos(mousePos[0] - 27, mousePos[1] - 27)
                if brush == "fill":

                    if not bitmap[bitmapPos.x, bitmapPos.y]:
                        fillDown = True
                        fillShape(bitmap, bitmapPos, 1)
                        pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (bitmapSize, bitmapSize)))
                        for y in range(bitmapSize):
                            for x in range(bitmapSize):
                                if bitmap[x, y]:
                                    pyg.draw.rect(display, white, pyg.Rect((x + 27, y + 27), (1, 1)))
                    else:
                        mouseDown = False

                elif brush == "eraser":

                    if not emptyBitmap:
                        pyg.draw.circle(display, darkgrey, mousePos, 12)
                        drawDot(bitmap, bitmapPos, 12, True)

                        if bitmapPos.x not in range(12, bitmapSize - 12):
                            pyg.draw.rect(display, white, pyg.Rect((25, 25), (2, bitmapSize + 4)))
                            pyg.draw.rect(display, white, pyg.Rect((539, 25), (2, bitmapSize + 4)))
                        if bitmapPos.y not in range(12, bitmapSize - 12):
                            pyg.draw.rect(display, white, pyg.Rect((25, 25), (bitmapSize + 4, 2)))
                            pyg.draw.rect(display, white, pyg.Rect((25, 539), (bitmapSize + 4, 2)))
                    else:
                        mouseDown = False

                else:
                    pyg.draw.circle(display, white, mousePos, brush)
                    drawDot(bitmap, bitmapPos, brush)

                    if bitmapPos.x not in range(brush, bitmapSize - brush):
                        pyg.draw.rect(display, darkgrey, pyg.Rect((10, 10), (15, 546)))
                        pyg.draw.rect(display, darkgrey, pyg.Rect((541, 10), (15, 546)))
                    if bitmapPos.y not in range(brush, bitmapSize - brush):
                        pyg.draw.rect(display, darkgrey, pyg.Rect((10, 10), (546, 15)))
                        pyg.draw.rect(display, darkgrey, pyg.Rect((10, 541), (546, 15)))

            elif mouseDown or fillDown:

                if len(buttons) == 7:
                    buttons.append(clearButton)
                if len(buttons) == 8:
                    buttons.append(submitButton)
                    
                bitmapBackups.append(copyBitmap(bitmap))
                if len(bitmapBackups) > 50:
                    del bitmapBackups[0]
                mouseDown = False
                fillDown = False

            action, running = detectAction(buttons)
            if action == "submit":

                # Disable the "Submit" button
                buttons.remove(submitButton)
                submitButton.setColor(lightgrey)

                # Reset progress bar
                pyg.draw.rect(display, darkgrey, pyg.Rect((703, 27), (364, 20)))

                # Reset shape guesses
                pyg.draw.rect(display, darkgrey, pyg.Rect((618, 108), (476, 558)))

                # Show text
                display.blit(smallFont.render("FigurAI thinks this shape is a:", 1, white), (696, 158))

                action, running = guessShape(bitmap, [buttons[0], clearButton])
                if action == "clear":
                    clearScreen = True

            if action == "clear":
                clearScreen = True
            elif action == "undo":
                if len(bitmapBackups) > 1:
                    bitmap = copyBitmap(bitmapBackups[-2])
                    del bitmapBackups[-2:]
                    pyg.draw.rect(display, darkgrey, pyg.Rect((27, 27), (bitmapSize, bitmapSize)))
                    for y in range(bitmapSize):
                        for x in range(bitmapSize):
                            if bitmap[x, y]:
                                pyg.draw.rect(display, white, pyg.Rect((x + 27, y + 27), (1, 1)))
                    mouseDown = True
                    
                else:
                    clearScreen = True
            elif action[:5] == "brush":
                for i in range(2, 7):
                    if buttons[i].getAction() == action:
                        buttons[i].setPermColor(yellow)
                    else:
                        buttons[i].setPermColor(white)

                brush = action[6:]

                if brush != "eraser" and brush != "fill":
                    brush = int(action[6:])

    if action == "menu":
        mainMenu()

def helpScreen():

    display.fill(darkgrey)
    buttons = [
        TextButton(Pos(322, 566), (450, 80), "exit_menu", "Return to Main Menu", font)
    ]

    display.blit(bigFont.render("Info", 1, white), (505, 25))
    display.blit(smallFont.render("FigurAI - A shape recognition program", 1, white), (345, 120))
    display.blit(smallFont.render("This program allows you to train an AI using randomly generated shapes", 1, white), (165, 165))
    display.blit(smallFont.render("to improve the accuracy, then you can test the AI by drawing a shape.", 1, white), (180, 210))
    display.blit(smallFont.render("The AI will learn to recognize Circles, Triangles, Rectangles, Pentagons and Hexagons.", 1, white), (90, 255))
    display.blit(smallFont.render("Settings Help:", 1, white), (475, 340))
    display.blit(smallFont.render("Save Interval - Sets the time interval between automatic saves in training mode", 1, white), (125, 385))
    display.blit(smallFont.render("Rotation Steps - Sets the number of times the user-drawn shape will rotate in testing mode", 1, white), (70, 430))
    display.blit(smallFont.render("Reset Database - Resets the training progress for all the shapes", 1, white), (210, 475))

    running = True
    while running:
        action, running = detectAction(buttons)
            
    if action == "menu":
        mainMenu()

def settings():

    buttons = [
        TextButton(Pos(619, 566), (450, 80), "exit_menu", "Return to Main Menu", font),
        globalSettings.getButton(0),
        globalSettings.getButton(1),
        TextButton(Pos(347, 421), (400, 80), "reset", "Reset Database", font)
    ]

    applyButton = TextButton(Pos(25, 566), (450, 80), "apply", "Apply", font)

    rotationSteps = globalSettings.getRotationSteps()
    saveInterval = globalSettings.getsaveInterval()

    buttons[1].setPos(Pos(saveInterval + 488, 180))
    buttons[2].setPos(Pos(int((rotationSteps - 1) / 4) + 489, 300))

    resetScreen = True
    pressedButton = None
    running = True
    while running:

        if resetScreen:

            display.fill(darkgrey)
            display.blit(bigFont.render("Settings", 1, white), (460, 25))
            display.blit(font.render("Save Interval", 1, white), (100, 175))
            display.blit(font.render("Rotation Steps", 1, white), (100, 295))
            
            pyg.draw.rect(display, lightgrey, pyg.Rect((499, 195), (500, 10)))
            pyg.draw.rect(display, lightgrey, pyg.Rect((499, 315), (500, 10)))
            
            textRect = smallFont.render(str(saveInterval), 1, white)
            display.blit(textRect, textRect.get_rect(center = (464, 200)))
            textRect = smallFont.render(str(rotationSteps), 1, white)
            display.blit(textRect, textRect.get_rect(center = (464, 320)))

            applyButton.setColor(lightgrey)

            resetScreen = False

        mousePos = pyg.mouse.get_pos()
        if not pyg.mouse.get_pressed()[0]:
            if pressedButton:
                if len(buttons) == 4:
                    buttons.append(applyButton)
                pressedButton = None
        
        action, running = detectAction(buttons)
        
        if action == "apply":
            globalSettings.setRotationSteps(rotationSteps)
            globalSettings.setsaveInterval(saveInterval)
            applyButton.setColor(lightgrey)
            buttons.remove(applyButton)

        for button in buttons[1:3]:
            if action == button.getAction():
                pressedButton = button
                xOffset = mousePos[0] - pressedButton.getPos().x

        if pressedButton:
            pyg.draw.rect(display, darkgrey, pyg.Rect((489, pressedButton.getPos().y), (520, 40)))

            sliderValue = pressedButton.getPos().x - 489
            if pressedButton.getAction() == "set_saveInterval":
                saveInterval = sliderValue + 1
                pyg.draw.rect(display, lightgrey, pyg.Rect((499, 195), (500, 10)))
                pyg.draw.rect(display, darkgrey, pyg.Rect((439, 185), (50, 30)))
                textRect = smallFont.render(str(saveInterval), 1, white)
                display.blit(textRect, textRect.get_rect(center = (464, 200)))
                
            if pressedButton.getAction() == "set_rotationSteps":
                rotationSteps = (sliderValue + 1) * 4
                pyg.draw.rect(display, lightgrey, pyg.Rect((499, 315), (500, 10)))
                pyg.draw.rect(display, darkgrey, pyg.Rect((439, 305), (50, 30)))
                textRect = smallFont.render(str(rotationSteps), 1, white)
                display.blit(textRect, textRect.get_rect(center = (464, 320)))
            
            newPos = Pos(mousePos[0] - xOffset, pressedButton.getPos().y)
            if newPos.x < 489:
                newPos.x = 489
            if newPos.x > 988:
                newPos.x = 988
            pressedButton.setPos(newPos)

        if action == "reset":
            resetScreen = True
            subAction = warningScreen("Warning - This action cannot be undone!")
            if subAction == "continue":

                textScreen("Resetting weights...")
                        
                for shapeName in shapeList:
                    for shapeType in shapeTypes:
                        shapeID = shapeType + shapeName
                        shapes[shapeID].setWeights(numpy.full((weightRes, weightRes), 0, dtype=int))
                        shapes[shapeID].saveWeights()

            elif subAction == "quit":
                running = False
            
        if action == "menu":
            if len(buttons) == 5:
                subAction = warningScreen("Warning - You have unsaved changes!")
                if subAction == "continue":
                    mainMenu()
                elif subAction == "cancel":
                    running = True
                    resetScreen = True
            else:
                mainMenu()

def textScreen(text):

    display.fill(darkgrey)
    textRect = bigFont.render(text, 1, white)
    display.blit(textRect, textRect.get_rect(center = (int(windowSize[0] / 2), int(windowSize[1] / 2))))
    pyg.display.flip()

def warningScreen(text):

    buttons = [
        TextButton(Pos(314, 388), (225, 80), "exit_cancel", "No", font),
        TextButton(Pos(555, 388), (225, 80), "exit_continue", "Yes", font)
    ]
    pyg.draw.rect(display, white, pyg.Rect((297, 185), (500, 300)))
    pyg.draw.rect(display, darkgrey, pyg.Rect((299, 187), (496, 296)))
    textRect = smallFont.render(text, 1, white)
    display.blit(textRect, textRect.get_rect(center = (547, 235)))
    display.blit(smallFont.render("Are you sure you want to continue?", 1, white), (363, 300))

    running = True
    while running:
        action, running = detectAction(buttons)

    return action


# Other functions

def detectAction(buttons):

    mousePos = pyg.mouse.get_pos()
    for button in buttons:
        if button.detectHover(mousePos):
            button.setColor(yellow)
        else:
            button.resetColor()

    action = ""
    for event in pyg.event.get():
        if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button.detectHover(event.pos):
                    action = button.getAction()
    
        # Quit button
        if event.type == pyg.QUIT:
            action = "exit_quit"

    if action[:4] == "exit":
        action = action[5:]
        running = False
    else:
        running = True

    pyg.display.flip()
        
    return action, running

def insertionSort(array):
    
    for i in range(1, len(array)):
        currentValue = array[i]
        pos = i
        while pos > 0 and array[pos - 1][1] < currentValue[1]:
            array[pos] = array[pos - 1]
            pos -= 1
        array[pos] = currentValue

    return array

def displayWeights(weightmap, offsetPos):

    maxWeight = weightmap[0, 0]
    minWeight = weightmap[0, 0]
    for y in range(weightRes):
        for x in range(weightRes):
            if weightmap[x, y] > maxWeight:
                maxWeight = weightmap[x, y]
            if weightmap[x, y] < minWeight:
                minWeight = weightmap[x, y]
                
    brightnessScale = maxWeight - minWeight
    for y in range(weightRes):
        for x in range(weightRes):
            weightDiff = weightmap[x, y] - minWeight
            if weightDiff != 0:
                brightness = int(weightDiff / brightnessScale * 255)
            else:
                brightness = 0
            pyg.draw.rect(display, (brightness, brightness, brightness), pyg.Rect((x * 2 + offsetPos.x, y * 2 + offsetPos.y), (2, 2)))

def displayBitmap(bitmap, offsetPos):

    bitmapRes = len(bitmap)
    pyg.draw.rect(display, darkgrey, (offsetPos.x, offsetPos.y, bitmapRes, bitmapRes))
    
    for x in range(bitmapRes):
        for y in range(bitmapRes):
            if bitmap[x, y]:
                pyg.draw.rect(display, white, (x + offsetPos.x, y + offsetPos.y, 1, 1))

def displayResults(totals, finalRotation):
    
    pyg.draw.rect(display, darkgrey, pyg.Rect((618, 198), (486, 368)))
    maxTotal = 5000

    results = []
    for shapeName in shapeList:
        total = totals[shapeName]
        if total > maxTotal / 100:
            if total > maxTotal:
                total = maxTotal
            results.append((shapeName, total))

    if len(results) == 0:
        results = [("idk bro", 0)]
    else:
        results = insertionSort(results)
        
    for i in range(len(results)):
        if i == 0 and finalRotation:
            color = yellow
        else:
            color = white
        yOffset = int((i - len(results) / 2) * 50)
        textRect = font.render(results[i][0] + " (" + format(results[i][1] / maxTotal * 100, ".0f") + "%)", 1, color)
        display.blit(textRect, textRect.get_rect(center = (848, 373 + yOffset)))

def calcAccuracy(results):

    if len(results) > 0:
        total = 0
        for result in results:
            total += result
        accuracy = total / len(results) * 100
    else:
        accuracy = 0

    return accuracy



### Main Program

print("\nLaunching FigurAI...")
textScreen("Launching FigurAI...")

print("\nRetrieving weights from '" + dbFileName + "' database...")
shapes = {}
for i in range(len(shapeList)):
    shapeName = shapeList[i]
    for shapeType in shapeTypes:
        shapeID = shapeType + shapeName
        shapes[shapeID] = Shape(shapeName, shapeType, i + 2)
        shapes[shapeID].setWeights(readWeights(shapeID))
print("Successfully retrieved all weights")
    
mainMenu()
print("\nExiting...")
textScreen("Exiting...")
pyg.quit()
