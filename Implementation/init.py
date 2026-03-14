import pygame as pyg
import numpy
import os
pyg.init()

# Class definitions

class Pos:
    
    def __init__(this, x, y):
        
        this.x = x
        this.y = y

class Button:
    
    def __init__(this, pos, dimensions, action):

        this.__pos = pos
        this.__dimensions = dimensions
        this.__action = action
        this.__color = white

    def draw(this):

        pyg.draw.rect(display, this.__color, pyg.Rect((this.__pos.x, this.__pos.y), this.__dimensions))
        pyg.draw.rect(display, darkgrey, pyg.Rect((this.__pos.x + 2, this.__pos.y + 2), (this.__dimensions[0] - 4, this.__dimensions[1] - 4)))

    def detectHover(this, mousePos):

        if mousePos[0] in range(this.__pos.x, this.__pos.x + this.__dimensions[0]) and mousePos[1] in range(this.__pos.y, this.__pos.y + this.__dimensions[1]):
            hover = True
        else:
            hover = False
        
        return hover

    def getPos(this):

        return this.__pos

    def getDimensions(this, index):

        return this.__dimensions[index]

    def getAction(this):

        return this.__action

    def getColor(this):

        return this.__color

    def setPos(this, pos):

        this.__pos = pos

    def setColor(this, color):

        this.__color = color
        this.draw()

    def resetColor(this):

        this.setColor(white)

class TextButton(Button):

    def __init__(this, pos, dimensions, action, text, buttonFont):
        super().__init__(pos, dimensions, action)
        this.__text = text
        this.__font = buttonFont
        this.draw()

    def draw(this):

        super().draw()
        buttonTextRect = this.__font.render(this.__text, 1, this.getColor())
        display.blit(buttonTextRect, buttonTextRect.get_rect(center = (this.getPos().x + this.getDimensions(0) / 2, this.getPos().y + this.getDimensions(1) / 2)))

class BrushButton(Button):

    def __init__(this, pos, dimensions, action):
        super().__init__(pos, dimensions, action)
        this.__whiteImg = pyg.image.load(assetFolder + action + "_white.png")
        this.__yellowImg = pyg.image.load(assetFolder + action + "_yellow.png")
        this.__permColor = white
        this.draw()

    def draw(this):

        super().draw()
        if this.getColor() == white:
            display.blit(this.__whiteImg, (this.getPos().x + 2, this.getPos().y + 2))
        else:
            display.blit(this.__yellowImg, (this.getPos().x + 2, this.getPos().y + 2))

    def setPermColor(this, color):

        this.__permColor = color

    def resetColor(this):

        this.setColor(this.__permColor)

class Settings:

    def __init__(this, saveInterval, rotationSteps):

        this.__saveInterval = saveInterval
        this.__rotationSteps = rotationSteps
        this.__buttons = [
            Button(Pos(0, 0), (20, 40), "set_saveInterval"),
            Button(Pos(0, 0), (20, 40), "set_rotationSteps")
        ]

    def getsaveInterval(this):

        return this.__saveInterval

    def getRotationSteps(this):

        return this.__rotationSteps

    def getButton(this, index):

        return this.__buttons[index]

    def setsaveInterval(this, saveInterval):

        this.__saveInterval = saveInterval

    def setRotationSteps(this, rotationSteps):

        this.__rotationSteps = rotationSteps
        
# Program settings

windowSize = [1094, 671]
smallFontSize = 24
fontSize = 48
bigFontSize = 64
titleFontSize = 100
darkgrey  = ( 32,  32,  32)
lightgrey = (128, 128, 128)
white     = (255, 255, 255)
yellow    = (245, 237,  85)
green     = ( 78, 211,  78)

globalSettings = Settings(5, 100)
shapeList = ["Circle", "Triangle", "Rectangle", "Pentagon", "Hexagon"]
shapeTypes = ["Hollow_", "Partial_", "Filled_"]
assetFolder = os.path.dirname(__file__) + "\\assets\\"
dbFileName = assetFolder + "weights.db"
shapeRes = 256 # Sets the resolution of the shapes that get randomly generated
weightRes = 64 # Sets the resolution of the weights for the shapes

pyg.display.set_caption("FigurAI")
display = pyg.display.set_mode(windowSize)
smallFont = pyg.font.Font(assetFolder + "AsapFont.ttf", smallFontSize)
font = pyg.font.Font(assetFolder + "BebasNeueFont.ttf", fontSize)
bigFont = pyg.font.Font(assetFolder + "BebasNeueFont.ttf", bigFontSize)
titleFont = pyg.font.Font(assetFolder + "StretchProFont.otf", titleFontSize)
