import pygame
import math
from queue import PriorityQueue

# annotated guide to Tech with Tim's A* pathfinding visualisation

# setting up pygame display
width = 800
win = pygame.display.set_mode((width, width))
pygame.display.set_caption("A* Path Finding Algorithm")

# colours for each element in the visualisation

red = (255,0,0) # closed path
green = (0,255,0) # open path
blue = (0,0,255) 
yellow = (255,255,0)
white = (255,255,255) # empty node
black = (0,0,0) # barrier
purple = (128,0,128)
orange = (255,165,0) # start node
grey = (128,128,128) # lines on grid
turquoise = (64,224,208) # end node

#Class describing each node(square) on the grid
class Node:

    def __init__(self, row, col, width, total_rows): # initialising with row and col position, and starting as empty
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.colour = white
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): # returns position of node
        return self.row, self.col

    # functions return True depending on type of node
    def is_closed(self):
        return self.colour == red

    def is_open(self):
        return self.colour == green

    def is_barrier(self):
        return self.colour == black

    def is_start(self):
        return self.colour == orange

    def is_end(self):
        return self.colour == turquoise

    # functions change type of node
    def reset(self):
        self.colour = white

    def make_closed(self):
        self.colour = red

    def make_open(self):
        self.colour = green

    def make_barrier(self):
        self.colour = black

    def make_start(self):
        self.colour = orange

    def make_end(self):
        self.colour = turquoise
    
    def make_path(self):
        self.colour = purple
    
    #draws the node given parameters
    def draw(self, win):
        pygame.draw.rect(win, self.colour,(self.x, self.y, self.width, self.width))

    # defines the neighbours of the node, given they are not barrier types
    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #down
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #up
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #right
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #left
            self.neighbours.append(grid[self.row][self.col - 1])            

    #???
    def __lt__(self, other):
        return False

#function for calculating H-number for A* algorithm
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# colours the path when the algorithm is finished
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# function computes A* algorithm
# https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
def algorithm(draw, grid, start, end):
    count = 0 #count of node being checked, for PriorityQueue
    open_set = PriorityQueue() #nodes to be checked, using priorityQueue based on count variable i.e. (count, data) insertion
    open_set.put((0, count, start)) # inserts into Priority queue, the zero is to make the queue infinite
    came_from = {} #defines the previous neighbour nodes which the current node came from
    g_score = {node: float("inf") for row in grid for node in row} # make all g anf f scores inf at start
    g_score[start] = 0 # distance from start node is 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos()) # heuristic distance calculated for start

    open_set_hash = {start} #nodes that have already been checked

    while not open_set.empty(): #can be quit while algorithm is running
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2] #refers to current node being checked
        open_set_hash.remove(current)

        if current == end: #if the algorithm reaches the end:
            reconstruct_path(came_from, end, draw)# the path is constructed
            start.make_start()
            end.make_end()
            return True
        
        for neighbour in current.neighbours: # g Score is the distance from the current node to the start node
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]: #if g score is optimal from neighbours
                came_from[neighbour] = current # replaces neighbour in optimal path
                g_score[neighbour] = temp_g_score #replaces neighbour g score and f score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash: #neighbour added to normal set with lower priority and added to hash set
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_closed()
        
        draw()

        if current != start:
            current.make_closed()
        
    return False


#function creates the grid pattern
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid


#function draws the grid lines
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, grey, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, grey, (j * gap, 0), (j * gap, width))


#funtion draws and displays the whole grid
def draw(win, grid, rows, width):
    win.fill(white)

    for row in grid:
        for node in row:
            node.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()


#function returns row, col position of click
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

#main function
def main(win, width):
    rows = 50
    grid = make_grid(rows, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started: #no user changes can be made while algorithm is running
                continue

            if pygame.mouse.get_pressed()[0]: #left mouse button
                pos = pygame.mouse.get_pos() # user adds start and end nodes, then can add barrier nodes
                row, col = get_clicked_pos(pos, rows, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                
                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()
            
            elif pygame.mouse.get_pressed()[2]: #right mouse button
                pos = pygame.mouse.get_pos() # reset any node back to empty (white)
                row, col = get_clicked_pos(pos, rows, width)
                node = grid[row][col]
                node.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end: #spacebar pressed and start and end nodes exist, then the algorithm will start
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    
                    algorithm(lambda: draw(win, grid, rows, width), grid, start, end)
            
                if event.key == pygame.K_c: #reset all nodes to empty with c
                    start = None
                    end = None
                    grid = make_grid(rows, width) 

    
    pygame.quit()

main(win, width)