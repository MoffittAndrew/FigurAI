# FigurAI

### Q: What is this?
A: Just a simple single-layer perceptron that can classify between different human-drawn shapes (circle, triangle, rectangle, pentagon, hexagon).
This was my high school final-year project, now uploaded here for the world to see :)

The fun part is that it is invariant to the position, scale, stretch-level, fill-level and even rotation of the shape - no matter what, it'll still (almost always) identify what shape you've drawn.

For more info, I recommend checking out the [FigurAI documentation](https://github.com/MoffittAndrew/FigurAI/blob/74f2f643ba8ab282d01d17489dd40ffc97b83ffc/Documentation/Documentation.pdf), it was part of my submission and gives some project background info and screenshots of it working.

### Q: Why?
A: Back in 2021, I watched a video explaining how perceptrons (basic single layer neural networks) worked, and I thought that was pretty cool so I made my own little perceptron ([RectangleCircleAI.py](https://github.com/MoffittAndrew/FigurAI/blob/74f2f643ba8ab282d01d17489dd40ffc97b83ffc/Archive/RectangleCircleAI.py)) that could distinguish between rectangles and circles in python.
When my final year of high school rolled around, I decided to challenge myself to turn this into a full python app that can recognize human-drawn shapes (instead of just computer generated ones with perfect straight lines) for my project, and to this day it is still my favourite project that I've ever worked on.

In the [Archive folder](https://github.com/MoffittAndrew/FigurAI/tree/74f2f643ba8ab282d01d17489dd40ffc97b83ffc/Archive), you can see the older versions of the project as it slowly developed into what it is now. Bear in mind that this was a fun project I did on the side during high school, before I really knew what I was doing with how to format code, how to structure projects, etc. - so don't judge the horrible code quality :(

### Q: What am I supposed to do with this?
A: The easiest way to run this project would probably be to download the [FigurAI.zip](https://github.com/MoffittAndrew/FigurAI/blob/1a68c7ad9f48d98a64d43d13a1fed72594e46250/FigurAI.zip) file, then extract and run FigurAI.py (in the Implementation folder). Or you can just poke around the code and laugh and how awful it is.

Note: This requires you to have the `pygame` and `sqlite3` python modules installed.