### NOTE from future Andrew - this code is also from 2021
### its basically a new and improved version of RectangleCircleAI.py

# Artificial intelligence program by Andrew Moffitt
# Generates a random shape, then trains a neuron network to figure out what shape got generated

def init():
    # Starts the program
    
    print("A simple artificial intelligence program to distinguish between a rectangle, circle, triangle or hexagon")
    hexagon_included = input("Would you like to include hexagons? (Y/N) ")
    repeat = input("Would you like the program to run in quick-learn mode? (Y/N) ")
    if repeat.upper() != "Y":
        repeat = "N"
        global latest_guesses
        latest_guesses = []
    
    return repeat.upper(), hexagon_included.upper()

def create_weights():
    # Creates a new weights.csv file
    
    weights = [shape_weight(0, 0, 0, 0)] * grid_base
    weights_file = open("weights.csv", "w", newline = "")
    write_file = csv.writer(weights_file)
    for index in range(grid_base):
        write_file.writerow([weights[index].rectangle, weights[index].circle, weights[index].triangle, weights[index].hexagon])
    weights_file.close()
    
    return weights

def read_file():
    # Reads from the weights.csv file into an array of records
    
    weights = []
    try:
        weights_file = open("weights.csv", "r")
    except:
        print("Error opening 'weights.csv' - File not found, creating a new one")
        weights = create_weights()
    else:
        read_file = csv.reader(weights_file)
        for record in read_file:
            weights.append(shape_weight(int(record[0]), int(record[1]), int(record[2]), int(record[3])))
        weights_file.close()
        
    return weights

def generate_shape(shape_gen, gen_hex):
    # Picks a random shape to generate

    if shape_gen == 0:
        shape = generate_rectangle()
        shape_type = "rectangle"
    elif shape_gen == 1:
        shape = generate_circle()
        shape_type = "circle"
    elif shape_gen == 2:
        shape = generate_triangle()
        shape_type = "triangle"
    elif gen_hex == "Y":
        shape = generate_hexagon()
        shape_type = "hexagon"

    return shape, shape_type

def generate_rectangle():
    # Generates a random rectangle (stored as a binary array)
    
    rectangle = [0] * grid_base
    corners = [
        randint(0, int(root_base / 4)),
        randint(0, int(root_base / 4)),
        randint(int((root_base / 2) + 1), int(root_base - 1)),
        randint(int((root_base / 2) + 1), int(root_base - 1))
    ]
    
    for loop in range(grid_base):
        x = loop % root_base
        y = int(loop / root_base)
        if x >= corners[0] and x <= corners[2] and y >= corners[1] and y <= corners[3]:
            rectangle[loop] = 1
    
    return rectangle

def generate_circle():
    # Generates a random circle
    
    circle = [0] * grid_base
    center = [
        randint(int(root_base / 3), int(root_base / 1.5)),
        randint(int(root_base / 3), int(root_base / 1.5))
    ]
    radius = randint(int(root_base / 8), int(root_base / 2))
    
    for loop in range(grid_base):
        x = loop % root_base
        y = int(loop / root_base)
        if ((x - center[0]) ** 2) + ((y - center[1]) ** 2) - (radius ** 2) < 1:
            circle[loop] = 1
    
    return circle

def generate_triangle():
    # Generates a random triangle
    
    triangle = [0] * grid_base
    corners = [
        randint(int(root_base / 4), int(root_base / 1.5)),
        randint(0, int(root_base / 4)),
        randint(0, int(root_base / 3)),
        randint(int(root_base / 2), int(root_base - 1)),
        randint(int((root_base / 2) + 1), int(root_base - 1))
    ]
    height = (corners[4] + 1) - corners[1]
    half_base = ((corners[3] + 1) - corners[2]) / 2

    for loop in range(grid_base):
        x = loop % root_base
        y = int(loop / root_base)
        width_gradient = (((y + 1) - corners[1]) / height) * half_base
        midline = half_base + ((root_base - y) * ((corners[0] - half_base) / height)) - (1 / height)
        if x >= (midline - width_gradient) and x < (midline + width_gradient) and y >= corners[1] and y <= corners[4]:
            triangle[loop] = 1
            
    return triangle

def generate_hexagon():
    # Generates a random hexagon
    
    hexagon = [0] * grid_base
    center = [
        randint(int(root_base / 3), int(root_base / 1.5)),
        randint(int(root_base / 3), int(root_base / 1.5))
    ]
    width = randint(int(root_base / 8), int(root_base / 2))
    height = cos30 * width
    
    for loop in range(grid_base):
        x = loop % root_base
        y = int(loop / root_base)
        if y <= center[1]:
            y_side = 1
        else:
            y_side = -1
        left_side = (center[0] - width) + (int(tan30 * (center[1] - y)) * y_side)
        right_side = (center[0] + width) + (int(tan30 * (center[1] - y)) * (0 - y_side))
        if x > left_side and x < right_side and y > (center[1] - height) and y < (center[1] + height):
            hexagon[loop] = 1
        
    return hexagon

def guess_shape(shape, weights, gen_hex):
    # Compares the shape to all the weights to guess what shape it is, whichever has the highest total is the program's guess
    
    totals = [0] * 4
    for loop in range(grid_base):
        totals[0] += (shape[loop] * weights[loop].rectangle)
        totals[1] += (shape[loop] * weights[loop].circle)
        totals[2] += (shape[loop] * weights[loop].triangle)
        if gen_hex == "Y":
            totals[3] += (shape[loop] * weights[loop].hexagon)
    
    highest_total = 0
    for loop in range(1, len(totals)):
        if totals[loop] > totals[highest_total]:
            highest_total = loop
    
    if highest_total == 0:
        shape_guess = "rectangle"
    elif highest_total == 1:
        shape_guess = "circle"
    elif highest_total == 2:
        shape_guess = "triangle"
    else:
        shape_guess = "hexagon"
    
    return shape_guess

def update_weights(shape, weights, shape_type, shape_guess, gen_hex):
    # Improves the weights

    weights_r = []
    weights_c = []
    weights_t = []
    weights_h = []
    for loop in range(grid_base):
        weights_r.append(weights[loop].rectangle)
        weights_c.append(weights[loop].circle)
        weights_t.append(weights[loop].triangle)
        weights_h.append(weights[loop].hexagon)
        
    if shape_type == "rectangle":
        weights_r = add_weights(shape, weights_r)
    elif shape_type == "circle":
        weights_c = add_weights(shape, weights_c)
    elif shape_type == "triangle":
        weights_t = add_weights(shape, weights_t)
    elif gen_hex == "Y":
        weights_h = add_weights(shape, weights_h)
        
    if shape_guess == "rectangle":
        weights_r = sub_weights(shape, weights_r)
    elif shape_guess == "circle":
        weights_c = sub_weights(shape, weights_c)
    elif shape_guess == "triangle":
        weights_t = sub_weights(shape, weights_t)
    elif gen_hex == "Y":
        weights_h = sub_weights(shape, weights_h)
        
    for loop in range(grid_base):
        weights[loop] = shape_weight(weights_r[loop], weights_c[loop], weights_t[loop], weights_h[loop])
        
    return weights

def add_weights(shape, weights):
    # Adds the generated shape to the weights
    
    for loop in range(grid_base):
        weights[loop] += shape[loop]
        
    return weights

def sub_weights(shape, weights):
    # Subtracts the generated shape from the weights
    
    for loop in range(grid_base):
        weights[loop] -= shape[loop]
        
    return weights

def update_file(weights):
    # Updates the weights.csv file
    
    weights_file = open("weights.csv", "w", newline = "")
    write_file = csv.writer(weights_file)
    for index in range(grid_base):
        write_file.writerow([weights[index].rectangle, weights[index].circle, weights[index].triangle, weights[index].hexagon])
    weights_file.close()

def display_shape(shape, shape_type):
    # Displays the shape
    
    if repeat == "N":
        print("\nRandomnly generated a " + shape_type + ":")
    
    print("/" + "-" * (root_base * 2 + 1) + "\\")
    for loop in range(root_base):
        line = "|"
        for x_pos in range(root_base):
            if shape[loop * root_base + x_pos] == 1:
                line += " O"
            else:
                line += "  "
        line += " |"
        print(line)
    print("\\" + "-" * (root_base * 2 + 1) + "/")

def calculate_accuracy(latest_guesses):
    # Calculates the most recent accuracy of the AI
    
    correct_guesses = 0
    for loop in range(len(latest_guesses)):
        if latest_guesses[loop] == "Correct":
            correct_guesses += 1
    accuracy = round((correct_guesses / len(latest_guesses)) * 100, 3)
    
    return accuracy
    



### Main program

# Imports packages and initialises global variables
from dataclasses import dataclass
from random import *
import csv
tan30 = (3 ** (1 / 2)) / 3
cos30 = (3 ** (1 / 2)) / 2
root_base = 256 # Sets the resolution of the shapes generated - higher values mean more accurate shapes/weights, but it will take longer for the program to learn them (Feel free to mess about with)
grid_base = root_base ** 2
update_loop = 1000 # Sets the amount of loops in quick-learn mode before updating the weight files/calculating percentage accuracy
latest_guesses = []
@dataclass
class shape_weight:
    rectangle: int
    circle: int
    triangle: int
    hexagon: int

weights = read_file()

loop_no = 0
repeat, gen_hex = init()

while True:

    if len(weights) != grid_base:
        print("There was a problem with 'weights.csv', resetting the weights")
        weights = create_weights()

    if gen_hex == "Y":
        random = randint(0, 3)
    else:
        random = randint(0, 2)
    shape, shape_type = generate_shape(random, gen_hex)
    shape_guess = guess_shape(shape, weights, gen_hex)
    
    if shape_guess != shape_type:
        guess = "Incorrect"
        weights = update_weights(shape, weights, shape_type, shape_guess, gen_hex)
    else:
        guess = "Correct"
    latest_guesses.append(guess)
    
    loop_no += 1
    if loop_no >= update_loop:
        loop_no = 0
        if repeat == "Y":
            #print("\nUpdated weights\n")
            accuracy = calculate_accuracy(latest_guesses)
            print("Accuracy: " + str(accuracy) + "%")
            latest_guesses = []
        if accuracy < 100:
            update_file(weights)
    
    if repeat == "N":
        display_shape(shape, shape_type)
        print("\nThe program guessed " + shape_guess + " (" + guess + ")")
        if guess == "Incorrect":
            update_file(weights)
        input()
input()
