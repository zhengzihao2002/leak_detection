import random
from collections import deque
import sys
import threading
import os

# Redirect stdout to null
original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
# Reset stdout back to its original value
sys.stdout = original_stdout
import time




"""寻找迷路的美羊羊"""



if len(sys.argv) != 3:
    # no parameters = default 50x50 ship with k=1
    arg1 = 50
    arg2 = 1
else:
    arg1 = int(sys.argv[1])
    arg2 = int(sys.argv[2])
    if arg2 < 1:
        print("Error: k Value must be greater than or equal to 1!")
        exit(0)






# the n*n matrix's size
n = arg1
# detection visibility -> k>=1
k = arg2

# -- Debug Mode -- 
debug = True
GUI_mode = True

# Auto Run In GUI
auto_run = True 
clicked = False # MUST BE FALSE NO MATTER WHAT
clicked_once = False # MUST BE FALSE NO MATTER WHAT 
interval = 0.3 # click every interval seconds

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
    



# global varibles and functions 
bot_location = None
leak_location= None
locations_for_leak_to_put = list() # cells outside detection square
possible_leak = list()
no_leak = list()
vincinty_cells = list()
leak_in_vincinty = False # current step, if leak is in detection square


def printShip(ship):
    global vincinty_cells
    detection_view = k
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
                    elif rowNum==leak_location[0] and colNum==leak_location[1]:
                        print("\033[95m" + "美" + "\033[0m",end=' ')
                        colNum+=1
                        continue
                    else:
                        # print("\033[92m" + "路" + "\033[0m",end=' ') #X
                        
                        if len(vincinty_cells)>0 and (rowNum,colNum) in vincinty_cells:
                            print("\033[93m" + "视" + "\033[0m",end=' ')
                        else:
                            print("\033[92m" + "路" + "\033[0m",end=' ')

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
def putBotAndLeak(ship,possible_leak_cells):
    # randomly choose a open space for leak and bot
    open_cells = list()
    for row in range(len(ship)):
        for col in range(len(ship[0])):
            if ship[row][col]==1:
                open_cells.append((row,col))
    bot = random.choice(open_cells)
    open_cells.remove(bot)

    # Filter out cells inside the detection square
    detection_view = k
    for cell in open_cells:
        valid = False
        if cell[1]>bot[1]+detection_view or cell[1]<bot[1]-detection_view:
            valid = True
        if cell[0]>bot[0]+detection_view or cell[0]<bot[0]-detection_view:
            valid = True
        if valid == True:
            possible_leak_cells.append(cell)
    if len(possible_leak_cells)<=0:
        # if no possible leak cells to get, any cell
        if debug:
            print("No valid cells outside detection square: getting a random cell inside square")
        possible_leak_cells = open_cells

    leak = random.choice(possible_leak_cells)
    open_cells.remove(leak)
    
    return [bot,leak]
def probability_check(probability):
    # returns True or False, given the probabailty. if given probability = 0.5, there is a 50/50 chance
    if 0 <= probability <= 1:
        return random.random() <= probability
    else:
        raise ValueError("Probability must be between 0 and 1")
def getVincity():
    vincity_cells = list()

    corner_coordinates = [(bot_location[0]-(k),bot_location[1]-(k)), (bot_location[0]-(k),bot_location[1]+(k)),(bot_location[0]+(k),bot_location[1]-(k)),(bot_location[0]+(k),bot_location[1]+(k))]

    # Find the minimum and maximum row and column values
    min_row = min(corner[0] for corner in corner_coordinates)
    max_row = max(corner[0] for corner in corner_coordinates)
    min_col = min(corner[1] for corner in corner_coordinates)
    max_col = max(corner[1] for corner in corner_coordinates)

    # Loop through and print the coordinates
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            if checkValidCell((row,col)):
                vincity_cells.append((row,col))
    # bot location is not a vincinty cell
    # vincity_cells.remove(bot_location)
    return vincity_cells
def detect_vincity():
    vincity_cells = getVincity()
    
    # now check if the vincinity cells have a leak. if so, return true. else false
    for cell in vincity_cells:
        if cell == leak_location:
            return True
    return False
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
def print_bright_yellow(text):
    # for debug purposes
    bright_yellow = "\033[93m"
    reset_color = "\033[0m"
    print(bright_yellow + text + reset_color)
def sense():
    if detect_vincity() == True:
        # Yes Leak
        global leak_in_vincinty 
        global vincinty_cells
        leak_in_vincinty = True
        # all cells are marked possibly leaking, if not in NO LEAK list
        vincinty_cells = getVincity()
        for cell in vincinty_cells:
            if cell not in no_leak:
                # only append cell is NOT marked as "no leak"
                possible_leak.append(cell)

        # cells outside of vincinty marked as not leaking
        rowNum = 0
        for row in ship:
            colNum = 0
            for element in row:
                if element == 1 and (rowNum,colNum) not in vincinty_cells:
                    # this is a cell outside of vincinty
                    if (rowNum,colNum) not in no_leak:
                        no_leak.append((rowNum,colNum))
                colNum+=1
            rowNum+=1
    else:
        # No Leak
        vincinty_cells = getVincity()
        # all cells in vincinty are marked as not leaking
        for cell in vincinty_cells:
            if cell not in no_leak:
                no_leak.append(cell)
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






















# STAGE 2: put bot and leak
bot_location,leak_location=putBotAndLeak(ship,locations_for_leak_to_put)
if debug:
    printShip(ship)

if debug:
    print_bright_yellow("寻找迷路的美羊羊：沸羊羊要在迷雾重重的森林里寻找美羊羊！")














# STAGE 3: Initializing before moving

# mark current cell as NO LEAK
no_leak.append(bot_location)



"""
---------- Detect Vincity ----------
No leak: all vincity cells marked NO LEAK
Yes Leak: all vincity cells marked POSSIBLE LEAK + all cells outside as NO LEAK
"""
sense()

if debug and not GUI_mode:
    print("possible leak",possible_leak)
    print("no leak",no_leak)












# STAGE 4: Bot moves
"""
At each timestep - the bot must choose whether to move or to sense.

When bot enters a cell, if it is not the leak cell, mark as not containing the leak. 

If the bot detects no leak in proximity - all cells in the detection square are marked as not containing the leak. 

If the bot detects a leak in proximity - all cells in the detection square not already marked as not containing the leak are marked as possibly containing the leak, and all cells outside the detection square are marked as not containing the leak.
"""
previous_step_moved:bool = False
BFS_in_progress:bool = False
BFS_route:list = None 
num_actions=0
visited_cells: list[list[tuple[int, int], int]] = list()
try:
    if auto_run:
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
                    x, y = j * CELL_SIZE[0], i * CELL_SIZE[1]
                    pygame.draw.rect(screen, (255, 255, 255), (x, y, CELL_SIZE[0], CELL_SIZE[1]))
                    if ship[i][j] == 0:
                        # closed cell
                        screen.blit(htl_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif (i,j)== leak_location and (i,j) == bot_location:
                        # bot and leak together
                        screen.blit(fm_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif (i, j) == bot_location:
                        # bot
                        screen.blit(fyy_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif (i, j) == leak_location:
                        # leak
                        screen.blit(myy_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
                    elif len(vincinty_cells)>0 and (i,j) in vincinty_cells:
                        # detection square
                        if leak_in_vincinty:
                            # Leak in vincity
                            pygame.draw.rect(screen, (0,204,102), (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05, CELL_SIZE[0] * 0.9, CELL_SIZE[1] * 0.9))
                        else:
                            pygame.draw.rect(screen, sense_color, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05, CELL_SIZE[0] * 0.9, CELL_SIZE[1] * 0.9))
                    elif len(no_leak)>0 and (i,j) in no_leak:
                        # noleak cells
                        pygame.draw.rect(screen, (160,160,160), (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05, CELL_SIZE[0] * 0.9, CELL_SIZE[1] * 0.9))
                    else:
                        pygame.draw.rect(screen, tan, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05, CELL_SIZE[0] * 0.9, CELL_SIZE[1] * 0.9))
            # Draw button
            button_color = (200, 200, 200)
            pygame.draw.rect(screen, button_color, (0, grid_height, WIDTH, button_height))
            if auto_run and GUI_mode:
                button_text = font.render("退出", True, (0, 0, 0))
            else:
                button_text = font.render("继续", True, (0, 0, 0))
            screen.blit(button_text, (WIDTH // 2 - 24, grid_height + button_height // 2 - 12))
            pygame.display.update()

        # Game Logic (runs if we click in GUI, or every time if no GUI)
        if clicked or not GUI_mode:
            if auto_run and GUI_mode and clicked_once:
                pygame.quit()
                time.sleep(0.40)
                sys.exit()
            # All game logic here
            num_actions+=1
            if bot_location not in visited_cells:
                visited_cells.append([bot_location,1])
            else:
                increase_visited_count(visited_cells,bot_location)
            # CHECK current cell, then choose to MOVE or to SENSE
            if debug and not GUI_mode:
                printShip(ship)
                print("possible leak",possible_leak)
                print("no leak",no_leak)
            if bot_location==leak_location:
                # Leak Found: break the loop
                break
            else:
                # Not leak cell: append into NO LEAK list
                if bot_location not in no_leak:
                    no_leak.append(bot_location)
                # remove cell from POSSIBLE LEAK list (if it exists within)
                if bot_location in possible_leak:
                    possible_leak.remove(bot_location)
            
            if BFS_in_progress:
                # Suppose a cell has no POSSIBLE LEAK neighbors, the bot will find a route any possible leak neighbor, and go to it using BFS
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

            
            if leak_in_vincinty:
                # bot chooses to MOVE each time
                # Leak nearby: bot moves only in vincinty cells until leak is found
                
                # USE BFS to go to any possible leak cell
                BFS_route = BFS(possible_leak[0])
                BFS_in_progress = True
                if debug:
                    print("4. MOVE to: ",BFS_route[0])
                move(BFS_route.pop(0))
                if len(BFS_route) == 0:
                    BFS_in_progress = False
            else:
                # bot chooses to MOVE/SENSE based the opposite of the previous move

                # Leak unknown: if there is no enough information on no leak cells, bot moves at random (up/down/left/right). Otherwise, bot will try to move away from the cells marked as NO LEAK -> Randomly choose between L/R/T/B that are IN possible leak
                if previous_step_moved:
                    # moved last step, SENSE this step
                    previous_step_moved = False
                    if debug:
                        print("SENSE")
                    sense()
                else:
                    # sensed last step, MOVE this step
                    previous_step_moved = True
                    neighbors = returnCoordinateOfAllValidNeighbors(ship,bot_location[0],bot_location[1])
                    favorable_neighbors = list()
                    for neighbor in neighbors:
                        if neighbor not in no_leak:
                            favorable_neighbors.append(neighbor)
                    if len(favorable_neighbors)>0:
                        # we have a neighbor that is not visited yet
                        picked_neighbor = random.choice(favorable_neighbors)
                        if debug:
                            print("5. MOVE to: ",picked_neighbor)
                        move(picked_neighbor)
                    else:
                        # dont waste time fucking with visited cells. find its way to any cell not in no leak list
                        BFS_route = find_nearest_cell_unvisited(bot_location,no_leak)
                        BFS_in_progress = True
                        if debug:
                            print("6. MOVE to: ",BFS_route[0])
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