import random
from collections import deque
import sys
import threading
import os
import math


# Redirect stdout to null
original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
# Reset stdout back to its original value
sys.stdout = original_stdout
import time



# game title
"""寻找迷路的美羊羊"""


# Get command line arguments
if len(sys.argv) != 3:
    # no parameters = default 50x50 ship with α=1
    arg1 = 50
    arg2 = 0
else:
    arg1 = int(sys.argv[1])
    arg2 = int(sys.argv[2])
    if arg2<0 or arg2>5:
        print("Error: alpha must be between the range [0-5] inclusive")
        exit(0)






# the n*n matrix's size
n = arg1
# α between [0-5]
alpha = arg2

# -- Debug Mode -- 
debug = True
GUI_mode = True

# Auto Run In GUI
auto_run = True 
clicked = False # MUST BE FALSE NO MATTER WHAT
clicked_once = False # MUST BE FALSE NO MATTER WHAT 
interval = 0.3 # click every interval seconds


# The SHIP
if debug == False:
    ship = []
else:
    # ***** COMMENT OUT ONE OF THE BELOW!!! *****


    """Unset Ship"""
    ship = []



    """Preset Ship"""
    # ship = [
    #     [1, 1, 1, 1, 1],
    #     [0, 0, 1, 0, 1],
    #     [1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 0],
    #     [1, 1, 0, 1, 1]
    # ]
    # n=len(ship[0])




# Entertainment Code
if debug:
    # Music
    pygame.init()
    pygame.mixer.init()
    file_path = 'extra/xyy.mp3'
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(-1)
    # GUI
    if GUI_mode:
        font = pygame.font.Font('extra/fireflysung.ttf', 24)
        WIDTH, HEIGHT = 800, 800
        ROWS, COLS = n,n
        button_height = HEIGHT // 10
        grid_height = HEIGHT - button_height
        CELL_SIZE = (WIDTH // COLS, grid_height // ROWS)
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("寻找迷路的美羊羊")
        # Miscellanous
        fyy_image = pygame.image.load('extra/fyy.jpeg')
        fyy_image = pygame.transform.scale(fyy_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
        myy_image = pygame.image.load('extra/myy.jpeg')
        myy_image = pygame.transform.scale(myy_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
        htl_image = pygame.image.load('extra/htl.jpeg')
        htl_image = pygame.transform.scale(htl_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
        fm_image = pygame.image.load('extra/fm.jpeg')
        fm_image = pygame.transform.scale(fm_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
        tan = (210, 180, 140)
        sense_color = (210, 210, 140)
    



# GLOBAL VARIABLES AND FUNCTIONS
bot_location = None
leak_location= None
leak_probability = list()



def printShip(ship):
    # outputs the ship in the terminal
    rowNum = 0
    for row in ship:
        colNum = 0
        for element in row:
            # if there is a bot and fire
            if bot_location!=None and leak_location!=None:
                if element == 1:
                    if rowNum==bot_location[0] and colNum==bot_location[1]:
                        print("\033[96m" + "沸" + "\033[0m",end=' ')
                        colNum+=1
                        continue
                    # BOT8 : need 2 leak locations
                    elif (rowNum,colNum)==leak_location[0] or (rowNum,colNum)==leak_location[1]:
                        print("\033[95m" + "美" + "\033[0m",end=' ')
                        colNum+=1
                        continue
                    else:
                        print("\033[92m" + "路" + "\033[0m",end=' ') #X
                        
                        colNum+=1
                else:
                    print("墙",end=' ')
                    colNum+=1
            # if there is no bot and fire
            else:    
                if element == 1:
                    print("\033[92m" + "路" + "\033[0m",end=' ')
                else:
                    print("墙",end=' ')
        rowNum+=1
        print()
def printProbList():
    for row in leak_probability:
        for element in row:
            # print(element,end=' ')
            percentage = element * 100
            print(f'{percentage:.4f}%', end=' ')
        print()

def checkCoordinateInBound(row,col):
    # checks if the given coordinate is in the bounds of the ship
    if row>=0 and row<n and col>=0 and col<n:
        return True
    return False
def checkValidCell(cell):
    # check if the coordinate is in bound, and if the cell is open
    if checkCoordinateInBound(cell[0],cell[1]) == True and ship[cell[0]][cell[1]]==1:
        return True
    return False
def countClosedNeighbors(ship,row,col):
    # returns the number of neighbors that are closed (used to determine dead ends) 

    neighbor_count = 0
    # top neighbor
    if checkCoordinateInBound(row-1,col)== True and ship[row-1][col]==0:
        neighbor_count += 1
    # bottom neighbor
    if checkCoordinateInBound(row+1,col)== True and ship[row+1][col]==0:
        neighbor_count += 1
    # left neighbor
    if checkCoordinateInBound(row,col-1)== True and ship[row][col-1]==0:
        neighbor_count += 1
    # right neighbor
    if checkCoordinateInBound(row,col+1)== True and ship[row][col+1]==0:
        neighbor_count += 1
    return neighbor_count
def checkIfDudeHasOnlyOneFriend(row, col, ship):
    # checks if a cell only have one open neighbor

    if ship[row][col] == 1:
        return False
    # Get the dimensions of the grid
    num_rows = len(ship)
    num_cols = len(ship[0])

    # Count the number of adjacent friends (assuming friends are represented by 1)
    adjacent_friends = 0

    # Check the friend to the left
    if col > 0 and ship[row][col - 1] == 1:
        adjacent_friends += 1

    # Check the friend to the right
    if col < num_cols - 1 and ship[row][col + 1] == 1:
        adjacent_friends += 1

    # Check the friend above
    if row > 0 and ship[row - 1][col] == 1:
        adjacent_friends += 1

    # Check the friend below
    if row < num_rows - 1 and ship[row + 1][col] == 1:
        adjacent_friends += 1

    # Return True if there is exactly one adjacent friend, otherwise False
    return adjacent_friends <= 1
def returnCoordinateOfAllValidNeighbors(ship:list,row:int,col:int,validDeterminant:int=1):
    # returns a list of coordinates of all the valid neighbors a cells has

    result = list()
    # top neighbor
    if checkCoordinateInBound(row-1,col)== True and ship[row-1][col]==validDeterminant:
        result.append((row-1,col))
    # bottom neighbor
    if checkCoordinateInBound(row+1,col)== True and ship[row+1][col]==validDeterminant:
        result.append((row+1,col))
    # left neighbor
    if checkCoordinateInBound(row,col-1)== True and ship[row][col-1]==validDeterminant:
        result.append((row,col-1))
    # right neighbor
    if checkCoordinateInBound(row,col+1)== True and ship[row][col+1]==validDeterminant:
        result.append((row,col+1))
    return result
def deadEnd(ship,row,col):
    # determines if a cell is considered a dead end

    valid_neighbors = 0
    if checkCoordinateInBound(row-1,col):
        valid_neighbors+=1
    if checkCoordinateInBound(row+1,col):
        valid_neighbors+=1
    if checkCoordinateInBound(row,col-1):
        valid_neighbors+=1
    if checkCoordinateInBound(row,col+1):
        valid_neighbors+=1
    
    if ship[row][col]==1 and countClosedNeighbors(ship,row,col) == valid_neighbors-1:
        return True
    return False
def putBotAndLeak(ship):
    # randomly choose a open space for leak and bot
    open_cells = list()
    for row in range(len(ship)):
        for col in range(len(ship[0])):
            if ship[row][col]==1:
                open_cells.append((row,col))
    bot = random.choice(open_cells)
    open_cells.remove(bot)


    # BOT8 : need 2 leaks
    leak1 = random.choice(open_cells)
    open_cells.remove(leak1)
    leak2 = random.choice(open_cells)
    open_cells.remove(leak2)
    
    return [bot,leak1,leak2]
def probability_check(probability):
    # returns True or False, given the probabailty. if given probability = 0.5, there is a 50/50 chance
    if 0 <= probability <= 1:
        return random.random() <= probability
    else:
        raise ValueError("Probability must be between 0 and 1")
def BFS(target_location,grid=ship):
    # BFS to find a path to the target
    rows, cols = len(grid), len(grid[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_valid(x, y):
        return checkCoordinateInBound(x,y) and grid[x][y] == 1 and not visited[x][y]

    queue = deque([(bot_location[0], bot_location[1], [])])
    visited[bot_location[0]][bot_location[1]] = True

    while queue:
        x, y, path = queue.popleft()
        if (x, y) == target_location:
            return path

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if is_valid(new_x, new_y):
                visited[new_x][new_y] = True
                new_path = path + [(new_x, new_y)]
                queue.append((new_x, new_y, new_path))
    if debug:
        print("No path is found! Bot location:",bot_location,"target_location:",target_location)
    return None  # If no path is found
def BFS_advanced(start_location,target_location):
    global ship
    # BFS to find a path to the target
    rows, cols = len(ship), len(ship[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_valid(x, y):
        return checkCoordinateInBound(x,y) and ship[x][y] == 1 and not visited[x][y]

    queue = deque([(start_location[0], start_location[1], [])])
    visited[start_location[0]][start_location[1]] = True

    while queue:
        x, y, path = queue.popleft()
        if (x, y) == target_location:
            return path

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if is_valid(new_x, new_y):
                visited[new_x][new_y] = True
                new_path = path + [(new_x, new_y)]
                queue.append((new_x, new_y, new_path))
    if debug:
        print("No path is found! start location:",start_location,"target_location:",target_location)
    return None  # If no path is found
def print_bright_yellow(text):
    # for debug purposes
    bright_yellow = "\033[93m"
    reset_color = "\033[0m"
    print(bright_yellow + text + reset_color)
def move(new_location:tuple):
    global bot_location
    bot_location = new_location
def pickMeACell(pick_from: list[tuple[int, int]], visitedList: list[list[tuple[int, int], int]]) -> tuple[int, int]:
    """
    Returns a unvisited cell based on the given list. If multiple, it randomly chooses between them. 
    If there are no unvisited cells, choose the least visited cell. 
    If multiple least visited cells, it randomly chooses between them.
    """

    # for each cell in pick_from, if the cell is not in the first element of for each element in visitedList -> put it in this list
    unvisited = [cell for cell in pick_from if cell not in [visited[0] for visited in visitedList]]
    
    # if unvisited list is not empty, we choose randomly
    if unvisited:
        return random.choice(unvisited)
    
    # Finds the minimum of the second element of each element in the visitedList -> aka Find the least visited count among cells
    min_visited = min(visitedList, key=lambda x: x[1])[1]

    # Loop through visitedList to find all cells with the minimum visited count -> Create list of least visited cells from visitedList that are also in pick_from
    least_visited = [visited[0] for visited in visitedList if visited[1] == min_visited and visited[0] in pick_from]
    
    # Return a random cell from the least visited cells.
    return random.choice(least_visited)
def increase_visited_count(visitedList, target_tuple):
    for sublist in visitedList:
        if sublist[0] == target_tuple:  # Check if the tuple matches
            sublist[1] += 1  # Increase the visited count by 1
            break  # Exit the loop
def find_nearest_cell_unvisited(start: tuple[int, int], no_leak: list[tuple[int, int]]) -> list[tuple[int, int]]:
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = deque([(start, [])])  # Each element is (location, path_so_far)
    visited = set()
    visited.add(start)
    parent = {}  # To keep track of the parent of each cell

    while queue:
        curr_location, path_so_far = queue.popleft()

        if curr_location not in no_leak:
            final_path = []
            while parent.get(curr_location):
                final_path.insert(0, curr_location)
                curr_location = parent[curr_location]
            return final_path

        for dx, dy in directions:
            x, y = curr_location
            next_location = (x + dx, y + dy)

            if next_location not in visited and checkValidCell(next_location):
                visited.add(next_location)
                parent[next_location] = curr_location
                queue.append((next_location, path_so_far + [curr_location]))
def reset_variable():
    global clicked
    while True:
        clicked = True
        time.sleep(interval)
def sense_beep(d):
    """
    returns T/F based on if beep is heard
    """
    result = math.exp(-alpha * (d - 1))
    return random.random() < result
def update_prob(type:str,curr_cell:tuple[int,int]):
    global leak_probability
    # Bot 8, the probability of hearing the beep (not not hearing the beep) must be updated taking the case that two leaks 
    """
    updates the probability based on the parameters
    - to update probability based on beep, pass BEEP to type
    - to update probability based on no beep, pass NOBEEP to type
    - to update probability based on move, pass MOVE to type
    
    - pass the coordinate of the current cell to curr_prob
    """
    if type == "BEEP":
        # Denominator
        sum = 0
        for row in range(len(leak_probability)):
            for col in range(len(leak_probability[row])):
                if (row,col) != curr_cell and ship[row][col]==1:
                    if total_leak == 1:
                        d = len(BFS_advanced(bot_location,leak_location[0]))
                        sum += (leak_probability[row][col] * (math.exp(-alpha*(d-1))))
                        continue
                    d = len(BFS_advanced(bot_location,leak_location[0]))
                    d2 = len(BFS_advanced(bot_location,leak_location[1]))
                    sum += (leak_probability[row][col] * (math.exp(-alpha*(d-1))) *  (math.exp(-alpha*(d2-1))))
        # Numerator combined with denominator
        for row in range(len(leak_probability)):
            for col in range(len(leak_probability[row])):
                if (row,col) != curr_cell and ship[row][col]==1:
                    if total_leak == 1:
                        d = len(BFS_advanced(bot_location,leak_location[0]))
                        sum += (leak_probability[row][col] * (math.exp(-alpha*(d-1))))
                        continue
                    d = len(BFS_advanced(bot_location,leak_location[0]))
                    d2 = len(BFS_advanced(bot_location,leak_location[1]))
                    leak_probability[row][col] = (leak_probability[row][col] * (math.exp(-alpha*(d-1))) *  (math.exp(-alpha*(d2-1)))) / sum
    if type == "NOBEEP":
        # Denominator
        sum = 0
        for row in range(len(leak_probability)):
            for col in range(len(leak_probability[row])):
                if (row,col) != curr_cell and ship[row][col]==1:
                    if total_leak == 1:
                        d = len(BFS_advanced(bot_location,leak_location[0]))
                        sum += (leak_probability[row][col] * (1-math.exp(-alpha*(d-1))))
                        continue
                    d = len(BFS_advanced(bot_location,leak_location[0]))
                    d2 = len(BFS_advanced(bot_location,leak_location[1]))
                    sum += (leak_probability[row][col] * (1-math.exp(-alpha*(d-1))) *  (1-math.exp(-alpha*(d2-1))))
        # Numerator combined with denominator
        for row in range(len(leak_probability)):
            for col in range(len(leak_probability[row])):
                if (row,col) != curr_cell and ship[row][col]==1:
                    if total_leak == 1:
                        d = len(BFS_advanced(bot_location,leak_location[0]))
                        sum += (leak_probability[row][col] * (1-math.exp(-alpha*(d-1))))
                        continue
                    d = len(BFS_advanced(bot_location,leak_location[0]))
                    d2 = len(BFS_advanced(bot_location,leak_location[1]))
                    leak_probability[row][col] = (leak_probability[row][col] * (1-math.exp(-alpha*(d-1))) *  (1-math.exp(-alpha*(d2-1)))) / sum
    elif type == "MOVE":
        curr_cell_prob = leak_probability[curr_cell[0]][curr_cell[1]]
        # for row in range(len(leak_probability)):
        #     for col in range(len(leak_probability[row])):
        #         if (row,col) != curr_cell:
        #             leak_probability[row][col] /= (1-curr_cell_prob)

        leak_probability = [
            [
                # If this cell is not the current cell, update its value
                val / (1 - curr_cell_prob) if (row, col) != curr_cell else val
                for col, val in enumerate(row_list)  # enumerate returns 2 values: col=index, val=element in row
            ]
            for row, row_list in enumerate(leak_probability)  # enumerate returns 2 values: row=index, row_list=row content
        ]
    else:
        # error
        return 0
def init_prob():
    ship_size = 0
    for row in ship:
        for element in row:
            if element == 1:
                ship_size += 1

    # initializes the ship to the initial probability
    # ship_size = n * n
    init_probability = 1 / ship_size

    global leak_probability
    leak_probability = []

    for row in ship:
        leak_row = []
        for cell in row:
            if cell == 1:
                # open cell : have a leak probability
                leak_row.append(init_probability)
            else:
                # closed cell : NO probability
                leak_row.append(0)
        leak_probability.append(leak_row)
    
    # Short handed way
    # leak_probability = [[init_probability if cell == 1 else 0 for cell in row] for row in ship]
def pickMeHighestProbability():
    global leak_probability
    global bot_location
    """
    returns the coordinate (binary tuple) of the cell that has the highest probability. if there is multiple cells that has the same highest probability, then pick the one with the shortest distance from the bot by calling len(BFS_advanced(start_location,target_location)), if multiple cells have same highest probability and same distance away from bot, then randomly choose between them
    """
    max_prob = -1
    highest_prob_cells = []
    
    for row in range(len(leak_probability)):
        for col in range(len(leak_probability[0])):
            if leak_probability[row][col] > max_prob and ship[row][col] == 1:
                max_prob = leak_probability[row][col]
                highest_prob_cells = [(row, col)]
            elif leak_probability[row][col] == max_prob and ship[row][col] == 1:
                highest_prob_cells.append((row, col))
                
    
    if len(highest_prob_cells) == 0:
        return None  # No open cell with the highest probability
    
    if len(highest_prob_cells) == 1:
        return highest_prob_cells[0]
    
    # Calculate distances if there are multiple cells with highest probability
    min_distance = 99999 # our ship is 50x50 so this works
    closest_cells = []
    
    for cell in highest_prob_cells:
        distance = len(BFS_advanced(bot_location, cell))
        if distance < min_distance:
            min_distance = distance
            closest_cells = [cell]
        elif distance == min_distance:
            closest_cells.append(cell)
            
    return random.choice(closest_cells)

    
    
    














# STAGE 1 -- Create a ship with a opened path
if ship == []:
    # creating a n*n matrix
    for i in range(n):
        row = []  # Create an empty row
        for j in range(n):
            row.append(0)  # Add elements to the row (initialize with zeros)
        ship.append(row)

    # Randomly generate the first node and place into queue
    init_row = random.randint(0, n - 1)
    init_col = random.randint(0, n - 1)
    open_list = list()
    open_list.append((init_row,init_col))

    # Loop that opens the nodes of the queue
    while len(open_list)>0:
        curr_node = random.choice(open_list)
        open_list.remove(curr_node)
        row, col = curr_node
        # before opening, check if it ONLY has 1 open neighbor (opend cells won't pass)
        if checkIfDudeHasOnlyOneFriend(row,col,ship)==False:
            continue
        # open it
        ship[row][col] = 1
        
        # Calculate the coordinates for the top, bottom, left, and right neighbors
        top = (row - 1, col)
        bottom = (row + 1, col)
        left = (row, col - 1)
        right = (row, col + 1)
            
        # Check if the top coordinate is valid
        if 0 <= top[0] < n and 0 <= top[1] < n:
            open_list.append(top)
            
        # Check if the bottom coordinate is valid
        if 0 <= bottom[0] < n and 0 <= bottom[1] < n:
            open_list.append(bottom)
            
        # Check if the left coordinate is valid
        if 0 <= left[0] < n and 0 <= left[1] < n:
            open_list.append(left)
            
        # Check if the right coordinate is valid
        if 0 <= right[0] < n and 0 <= right[1] < n:
            open_list.append(right)

        # if debug:
        #     printShip(ship)
        #     input("按回车键继续 ...")
else:
    # we only enter here if we are 1, in developer mode, 2, gave a specific matrix to ship
    printShip(ship)

if debug:
    printShip(ship)
    #input("按回车键继续 ...")

# Open 1/2 of the dead end cells' neighbors (Dead End: an OPEN cell that has exactly n-1 CLOSED neighbors, where n is number of valid neighbors. e.g. a closed cell with 4 adjacent cells with 3 OPEN is consider dead end) 
blocked_cells = list()
for row in range(len(ship)):
    for col in range(len(ship[0])):
        # for each cell count the number of neighbors
        valid_neighbors = 0
        if checkCoordinateInBound(row-1,col):
            valid_neighbors+=1
        if checkCoordinateInBound(row+1,col):
            valid_neighbors+=1
        if checkCoordinateInBound(row,col-1):
            valid_neighbors+=1
        if checkCoordinateInBound(row,col+1):
            valid_neighbors+=1
        
        # check if the cell is considered a dead end/blocked
        if ship[row][col]==1 and countClosedNeighbors(ship,row,col) == valid_neighbors-1:
            blocked_cells.append((row,col))
if len(blocked_cells)>0:
    if debug:
        print("The following are considered dead ends: ",blocked_cells)
    chosen_blocked_cells_to_open = list()
    actually_opened = list()
    for i in range(len(blocked_cells)//2):
        curr_node = random.choice(blocked_cells)
        blocked_cells.remove(curr_node)
        chosen_blocked_cells_to_open.append(curr_node)
    if debug:
        print("Opening the following dead ends: ",chosen_blocked_cells_to_open)
        #input("按回车键继续 ...")
    
    
    # open 1/2 of the dead end cells
    num = len(chosen_blocked_cells_to_open)
    for i in range(num):
        curr_node = random.choice(chosen_blocked_cells_to_open)
        chosen_blocked_cells_to_open.remove(curr_node)
        # check if it is STILL considered a dead end (cuz we might JUST opened a cell and it is no longer a dead end), if yes, open one of it's CLOSED neighbors. if not, fuck it!
        if deadEnd(ship,curr_node[0],curr_node[1]) == True:
            closed_neighbors = returnCoordinateOfAllValidNeighbors(ship,curr_node[0],curr_node[1],0)
            opening_cell = random.choice(closed_neighbors)
            actually_opened.append(opening_cell)
            ship[opening_cell[0]][opening_cell[1]] = 1
    if debug:
        print("Actually Opened Cells: ",actually_opened)
else:
    if debug:
        print("No dead ends to open")

if debug:
    printShip(ship)
    print("Stage 1 complete: Initial path and half of dead ends all opened")
    #input("按回车键继续 ...")






















# STAGE 2: put bot and leak into the ship
bot_location,leak_location1,leak_location2=putBotAndLeak(ship)
leak_location = [leak_location1,leak_location2] # BOT8 : two leaks
if debug:
    printShip(ship)
if debug:
    print_bright_yellow("寻找迷路的美羊羊：沸羊羊要在迷雾重重的森林里寻找美羊羊！")














# STAGE 3: Initializing before moving
init_prob()
# mark current cell's leak possiblity as zero
leak_probability[bot_location[0]][bot_location[1]] = 0

if debug and not GUI_mode:
    print("probability")
    printProbList()












# STAGE 4: Bot moves
"""
– At any time, the bot is going to move to the cell that has the highest probability of containing the leak (breaking ties first by distance from the bot, then at random).

– After entering any cell, if the cell does not contain a leak, the bot will take the sense action. Based on the results, it updates the probability of containing the leak for each cell.

– If the bot hears a beep, then the probability will be updated again
"""
BFS_in_progress:bool = False
BFS_route:list = None 
visited_cells: list[list[tuple[int, int], int]] = list()
total_leak = 2 # BOT8 : multiple leaks
num_actions = 0
try:
    if auto_run and GUI_mode:
        reset_thread = threading.Thread(target=reset_variable)
        reset_thread.daemon = True
        reset_thread.start()

    while True:
        # Update GUI
        if debug and GUI_mode:
            # GUI and Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if 0 <= mouse_x <= WIDTH and grid_height <= mouse_y <= HEIGHT:
                        clicked = True  
                        clicked_once = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z and event.mod & pygame.KMOD_CTRL:
                        pygame.quit()
                        sys.exit()
            for i in range(ROWS):
                for j in range(COLS):
                    # TODO add colors, green, yellow green, yellow, orange, red to represent probabilities
                    x, y = j * CELL_SIZE[0], i * CELL_SIZE[1]
                    pygame.draw.rect(screen, (255, 255, 255), (x, y, CELL_SIZE[0], CELL_SIZE[1]))
                    if ship[i][j] == 0:
                        # closed cell
                        screen.blit(htl_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif (i,j) in leak_location and (i,j) == bot_location: # BOT8 : multiple leaks
                        # bot and leak together
                        screen.blit(fm_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif (i, j) == bot_location:
                        # bot
                        screen.blit(fyy_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif (i, j) in leak_location: # BOT8 : multiple leaks
                        # leak
                        screen.blit(myy_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    else:
                        text_surface = font.render(str(leak_probability[i][j]), True, (0, 0, 0))
                        pygame.draw.rect(screen, tan, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05, CELL_SIZE[0] * 0.9, CELL_SIZE[1] * 0.9))
                        screen.blit(text_surface, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
            # Draw button
            button_color = (200, 200, 200)
            pygame.draw.rect(screen, button_color, (0, grid_height, WIDTH, button_height))
            if auto_run and GUI_mode:
                button_text = font.render("退出", True, (0, 0, 0))
            else:
                button_text = font.render("继续", True, (0, 0, 0))
            screen.blit(button_text, (WIDTH // 2 - 24, grid_height + button_height // 2 - 12))
            pygame.display.update()

        # Game Logic (runs if we click in GUI, or every time if not GUI mode)
        if clicked or not GUI_mode:
            if auto_run and GUI_mode and clicked_once:
                pygame.quit()
                time.sleep(0.40)
                sys.exit()
            # All game logic here
            num_actions+=1
            if debug and not GUI_mode:
                printShip(ship)
            if bot_location in leak_location: # BOT8 : multiple leaks
                # Leak Found: break the loop
                total_leak -=1 # BOT8 : multiple leaks
                leak_location.remove(bot_location)
                if total_leak == 0:
                    break
            # update probability since the current cell is not leak
            update_prob("MOVE",bot_location)
            printProbList()
            leak_probability[bot_location[0]][bot_location[1]] = 0
            if BFS_in_progress:
                if debug:
                    print("1. MOVE to: ",BFS_route[0])
                move(BFS_route.pop(0))
                if len(BFS_route) == 0:
                    BFS_in_progress = False
                if debug and GUI_mode:
                    while not clicked:
                        pass
                    clicked = False
                elif debug:
                    input("按回车键继续 ...")
                continue
            nearestLeak = None
            if len(leak_location)>1:
                if len(BFS_advanced(bot_location,leak_location[0])) <= len(BFS_advanced(bot_location,leak_location[1])):
                    nearestLeak = leak_location[0]
                else:
                    nearestLeak = leak_location[1]
            else:
                nearestLeak = leak_location[0]
            if(sense_beep(len(BFS_advanced(bot_location,nearestLeak)))):
                # Beep is sensed
                print("BEEP")
                update_prob("BEEP",bot_location)
                printProbList()
            else:
                # Beep is not sensed
                print("NOBEEP")
                update_prob("NOBEEP",bot_location)
                printProbList()
            new_location = pickMeHighestProbability()
            BFS_route = BFS(new_location)
            BFS_in_progress = True
            if debug:
                print("2. MOVE to: ",BFS_route[0], "target: ",new_location,"prob at target:",leak_probability[new_location[0]][new_location[1]])
            move(BFS_route.pop(0))
            if len(BFS_route) == 0:
                BFS_in_progress = False
            # Reset clicked flag
            clicked = False

        # Wait for User input
        if debug and not clicked and not GUI_mode:
            input("按回车键继续 ...")
except KeyboardInterrupt:
    # handle force quit
    pygame.quit()
    sys.exit()    




if debug:
    if(n<10):
        time.sleep(5)
    pygame.mixer.music.stop()
    pygame.quit()
    time.sleep(1)
    print_bright_yellow("沸羊羊成功找到了美羊羊！")
print("Total Actions: ",num_actions)