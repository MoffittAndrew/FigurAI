### NOTE from future Andrew - this code is from 2021

# Simple artificial intelligence program by Andrew Moffitt
# Generates a random rectangle or circle, then trains a neuron network to correctly guess which one it is

def init():
    # Starts the program
    print("A simple artificial intelligence program to distinguish between a rectangle and a circle")
    repeat = input("Would you like the program to run in repeat mode? (Y/N) ")
    return repeat.upper()

def create_weights():
    # Creates a new weights.txt file
    weights = [0] * 64
    weights_file = open("weights.txt", "w")
    for entry in weights:
        weights_file.write(str(entry) + "\n")
    weights_file.close()
    return weights

def read_file(weights):
    # Reads from the weights.txt file into an array
    try:
        weights_file = open("weights.txt", "r")
    except:
        print("No weights file was found, creating a new one")
        weights = create_weights()
    else:
        read_file = weights_file.read().splitlines()
        for loop in range(len(read_file)):
            weights.append(int(read_file[loop]))
        weights_file.close()
    return weights

def generate_rectangle():
    # Generates a random rectangle in an 8x8 grid (stored as an array)
    rectangle = [0] * 64
    corners = [randint(0,2),randint(0,2),randint(5,7),randint(5,7)]
    for loop in range(0,64):
        x = loop % 8
        y = int(loop / 8)
        if x >= corners[0] and x <= corners[2] and y >= corners[1] and y <= corners[3]:
            rectangle[loop] = 1
    return rectangle

def generate_circle():
    # Generates a random circle
    circle = [0] * 64
    center = [randint(3,4),randint(3,4)]
    radius = randint(1,4)
    for loop in range(0,64):
        x = loop % 8
        y = int(loop / 8)
        if ((x - center[0]) ** 2) + ((y - center[1]) ** 2) - (radius ** 2) < 1:
            circle[loop] = 1
    return circle

def guess_shape(shape,weights):
    # Compares the shape to the weights to guess what shape it is
    total = 0
    for loop in range(0,64):
        total += (shape[loop] * weights[loop])
    if total > bias:
        shape_guess = "rectangle"
    else:
        shape_guess = "circle"
    return shape_guess

def learn_shape(shape,weights):
    # Changes the weights
    if shape_guess == "rectangle":
        for loop in range(0,64):
            weights[loop] -= shape[loop]
    else:
        for loop in range(0,64):
            weights[loop] += shape[loop]
    weights_file = open("weights.txt", "w")
    for entry in weights:
        weights_file.write(str(entry) + "\n")
    weights_file.close()
    return weights

def display_shape(shape,shape_type):
    # Turns the array into an 8 x 8 grid
    if repeat == "N":
        print("\nThe program has randomnly generated a " + shape_type)
    for loop in range(0,8):
        line = []
        for x_pos in range(0,8):
            line.append(shape[loop * 8 + x_pos])
        print(line)
    
# Main program
from random import*
bias = 0
weights = []
weights = read_file(weights)
repeat = "y"
while repeat.upper() == "Y":
    if len(weights) != 64:
        print("There was a problem with the weights, resetting them")
        weights = create_weights()
    if repeat == "y":
        repeat = init()
    if randint(0,1) == 0:
        shape = generate_rectangle()
        shape_type = "rectangle"
    else:
        shape = generate_circle()
        shape_type = "circle"
    if repeat == "N":
        display_shape(shape,shape_type)
    shape_guess = guess_shape(shape,weights)
    if repeat == "N":
        print("The program guessed " + shape_guess + "\n")
    if shape_guess != shape_type:
        if repeat == "Y":
            print("Incorrect")
        weights = learn_shape(shape,weights)
    elif repeat == "Y":
        print("Correct")
input()
