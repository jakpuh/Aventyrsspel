import random

def Maze(width, height):
    maze = []
    for i in range(0, height):
        row = []
        for j in range(0, width):
            row.append("⬛")
        maze.append(row)
        
    x = random.randint(0, width)-1
    y = random.randint(0, height)-1
    maze[y][x] = "🔴"
    
    try:
        while True:
            rand = random.randint(0,3)
            if rand == 0:
                maze[y+1][x] = "🔴" 
                y += 1
            if rand == 1:
                maze[y][x+1] = "🔴"
                x += 1
            if rand == 2:
                maze[y-1][x] = "🔴"
                y -= 1
            if rand == 3:
                maze[y][x-1] = "🔴"
                x -= 1
    except:
        return maze



for i in Maze(3,3):
    print(i)