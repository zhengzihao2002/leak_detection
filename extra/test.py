import pygame

pygame.init()
font = pygame.font.Font('fireflysung.ttf', 24)
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 5,5
button_height = HEIGHT // 10
grid_height = HEIGHT - button_height
CELL_SIZE = (WIDTH // COLS, grid_height // ROWS)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("寻找迷路的美羊羊")


# Initialize 2D array, images, and positions
ship = [
    [1,1,1,1,1],
    [1,0,0,0,0],
    [1,1,1,0,0],
    [0,1,1,1,1],
    [0,0,0,0,1]
]
# ship = [[1, 1, 0, 0,0,0,0,0,0,0], 
#         [1, 1, 0, 1,0,0,0,0,0,0], 
#         [0, 1, 1, 1,0,0,0,0,0,0], 
#         [0, 0, 1, 1,0,0,0,0,0,0],
#         [0, 0, 1, 1,0,0,0,0,0,0],
#         [0, 0, 1, 1,0,0,0,0,0,0],
#         [0, 0, 1, 1,0,0,0,0,0,0],
#         [0, 0, 1, 1,0,0,0,0,0,0],
#         [0, 0, 1, 1,0,0,0,0,0,0],
#         [0, 0, 1, 1,0,0,0,0,0,0]]
fyy = (0, 0)
myy = (3, 3)






fyy_image = pygame.image.load('fyy.jpeg')
fyy_image = pygame.transform.scale(fyy_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
myy_image = pygame.image.load('myy.jpeg')
myy_image = pygame.transform.scale(myy_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
htl_image = pygame.image.load('htl.jpeg')
htl_image = pygame.transform.scale(htl_image, (int(CELL_SIZE[0] * 0.9), int(CELL_SIZE[1] * 0.9)))
tan = (210, 180, 140)


# Main loop
running = True
clicked = False  # Flag to control the loop

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if 0 <= mouse_x <= WIDTH and grid_height <= mouse_y <= HEIGHT:
                clicked = True  # Set flag to True when button is clicked

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw grid
    for i in range(ROWS):
        for j in range(COLS):
            x, y = j * CELL_SIZE[0], i * CELL_SIZE[1]

            pygame.draw.rect(screen, (255, 255, 255), (x, y, CELL_SIZE[0], CELL_SIZE[1]))

            if ship[i][j] == 0:
                screen.blit(htl_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
            elif (i, j) == fyy:
                screen.blit(fyy_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
            elif (i, j) == myy:
                screen.blit(myy_image, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05))
            else:
                pygame.draw.rect(screen, tan, (x + CELL_SIZE[0] * 0.05, y + CELL_SIZE[1] * 0.05, CELL_SIZE[0] * 0.9, CELL_SIZE[1] * 0.9))

    # Draw button
    button_color = (200, 200, 200)
    pygame.draw.rect(screen, button_color, (0, grid_height, WIDTH, button_height))
    button_text = font.render("继续", True, (0, 0, 0))
    screen.blit(button_text, (WIDTH // 2 - 24, grid_height + button_height // 2 - 12))

    if clicked:
        print("Clicked")
        clicked = False  # Reset the flag for the next iteration

    print("update")
    pygame.display.update()
