import pygame
import sys
import time
import math
import gamelogic as ttt
import random

pygame.init()

display_info = pygame.display.Info()
screen_width = min(display_info.current_w - 100, 1024)
screen_height = min(display_info.current_h - 100, 768)
size = width, height = screen_width, screen_height

black = (0, 0, 0)
gray = (90, 90, 90)
white = (241, 250, 238)
shadow = (50, 50, 50)  
light_blue = (173, 216, 230) 
green = (0, 200, 0) 
red = (200, 0, 0) 
blue = (0, 0, 200)
purple = (128, 0, 128)  

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Tic-Tac-Toe AI Game")

small_font_size = int(height * 0.05)
medium_font_size = int(height * 0.1)
large_font_size = int(height * 0.15)
move_font_size = int(height * 0.08)

smallFont = pygame.font.SysFont("Arial", small_font_size, bold=True)
mediumFont = pygame.font.SysFont("Arial", medium_font_size, bold=True)
largeFont = pygame.font.SysFont("Arial", large_font_size, bold=True)
moveFont = pygame.font.SysFont("Arial", move_font_size, bold=True)

user = None
difficulty = None  
board = ttt.initial_state()
ai_turn = False
animation_progress = 0  
winning_line = None  
winner_player = None  

def draw_3d_button(surface, rect, text, font, base_color, shadow_color, text_color, hover=False, selected=False):
    shadow_offset = int(height * 0.007)  
    border_radius = int(height * 0.017)  

    shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height)
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=border_radius)

    if selected:
        color = light_blue
    else:
        color = (min(base_color[0] + 20, 255), min(base_color[1] + 20, 255), min(base_color[2] + 20, 255)) if hover else base_color
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)

    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)

def get_winning_line(board):
    for i, row in enumerate(board):
        if row.count(row[0]) == 4 and row[0] is not ttt.EMPTY:
            return ("row", i)

    for j in range(4):
        column = [board[i][j] for i in range(4)]
        if column.count(column[0]) == 4 and column[0] is not ttt.EMPTY:
            return ("column", j)

    if all(board[i][i] == board[0][0] and board[i][i] is not ttt.EMPTY for i in range(4)):
        return ("diagonal", 0)

    if all(board[i][3 - i] == board[0][3] and board[i][3 - i] is not ttt.EMPTY for i in range(4)):
        return ("anti-diagonal", 0)

    return None

def draw_winning_line(surface, line_type, index, tiles, progress):
    if line_type == "row":
        start_pos = (tiles[index][0].left, tiles[index][0].centery)
        end_pos = (tiles[index][3].right, tiles[index][3].centery)
        current_end = (start_pos[0] + (end_pos[0] - start_pos[0]) * min(progress, 1.0), start_pos[1])
    elif line_type == "column":
        start_pos = (tiles[0][index].centerx, tiles[0][index].top)
        end_pos = (tiles[3][index].centerx, tiles[3][index].bottom)
        current_end = (start_pos[0], start_pos[1] + (end_pos[1] - start_pos[1]) * min(progress, 1.0))
    elif line_type == "diagonal":
        start_pos = (tiles[0][0].left, tiles[0][0].top)
        end_pos = (tiles[3][3].right, tiles[3][3].bottom)
        current_end = (start_pos[0] + (end_pos[0] - start_pos[0]) * min(progress, 1.0), 
                      start_pos[1] + (end_pos[1] - start_pos[1]) * min(progress, 1.0))
    elif line_type == "anti-diagonal":
        start_pos = (tiles[0][3].right, tiles[0][3].top)
        end_pos = (tiles[3][0].left, tiles[3][0].bottom)
        current_end = (start_pos[0] + (end_pos[0] - start_pos[0]) * min(progress, 1.0), 
                      start_pos[1] + (end_pos[1] - start_pos[1]) * min(progress, 1.0))
    
    line_width = int(height * 0.01) 
    pygame.draw.line(surface, green, start_pos, current_end, line_width)
    
    for i in range(3):
        glow_width = line_width - i * 2
        if glow_width > 0:
            glow_color = (green[0], min(green[1] + 20 * i, 255), green[2])
            pygame.draw.line(surface, glow_color, start_pos, current_end, glow_width)

def draw_move(surface, rect, move):
    padding = rect.width * 0.2
    inner_rect = pygame.Rect(rect.x + padding, rect.y + padding, 
                           rect.width - 2*padding, rect.height - 2*padding)
    
    if move == ttt.X:
        color = red
        line_width = max(3, int(rect.width * 0.05))
        pygame.draw.line(surface, color, 
                        (inner_rect.left, inner_rect.top), 
                        (inner_rect.right, inner_rect.bottom), line_width)
        pygame.draw.line(surface, color, 
                        (inner_rect.left, inner_rect.bottom), 
                        (inner_rect.right, inner_rect.top), line_width)
    else: 
        color = blue
        line_width = max(3, int(rect.width * 0.05))
        pygame.draw.ellipse(surface, color, inner_rect, line_width)

clock = pygame.time.Clock()  
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    for y in range(height):
        color_value = 70 + (y / height) * 40
        pygame.draw.line(screen, (color_value, color_value, color_value), (0, y), (width, y))

    if user is None:
        title_shadow = largeFont.render("Tic-Tac-Toe", True, shadow)
        title_shadow_rect = title_shadow.get_rect()
        title_shadow_rect.center = ((width / 2) + 5, height * 0.15 + 5)  
        screen.blit(title_shadow, title_shadow_rect)
        
        title = largeFont.render("Tic-Tac-Toe", True, purple)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), height * 0.15) 
        screen.blit(title, titleRect)

        lowertitle = smallFont.render("(Using pygame with AI)", True, white)
        titleRect = lowertitle.get_rect()
        titleRect.center = ((width / 2), height * 0.25) 
        screen.blit(lowertitle, titleRect)

        if difficulty is None:
            difficultyText = smallFont.render("Select Difficulty:", True, white)
            difficultyRect = difficultyText.get_rect()
            difficultyRect.center = ((width / 2), height * 0.35) 
            screen.blit(difficultyText, difficultyRect)

            button_width = width / 5
            button_height = height * 0.08
            button_y = height * 0.45 
            
            easyButton = pygame.Rect((width / 6), button_y, button_width, button_height)
            hover_easy = easyButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, easyButton, "Easy", smallFont, white, shadow, black, hover=hover_easy)

            mediumButton = pygame.Rect((width / 2 - button_width/2), button_y, button_width, button_height)
            hover_medium = mediumButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, mediumButton, "Medium", smallFont, white, shadow, black, hover=hover_medium)

            hardButton = pygame.Rect((width - width / 6 - button_width), button_y, button_width, button_height)
            hover_hard = hardButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, hardButton, "Hard", smallFont, white, shadow, black, hover=hover_hard)

            click, _, _ = pygame.mouse.get_pressed()
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if easyButton.collidepoint(mouse):
                    time.sleep(0.2)
                    difficulty = "easy"
                elif mediumButton.collidepoint(mouse):
                    time.sleep(0.2)
                    difficulty = "medium"
                elif hardButton.collidepoint(mouse):
                    time.sleep(0.2)
                    difficulty = "hard"
        else:
            difficultyText = smallFont.render(f"Difficulty: {difficulty.capitalize()}", True, white)
            difficultyRect = difficultyText.get_rect()
            difficultyRect.center = ((width / 2), height / 2 - 80)
            screen.blit(difficultyText, difficultyRect)

            button_width = width / 4
            button_height = height * 0.08
            button_y = height / 2
            
            playXButton = pygame.Rect((width / 8), button_y, button_width, button_height)
            hover_x = playXButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, playXButton, "Play as X", smallFont, red, shadow, white, hover=hover_x)

            playOButton = pygame.Rect(5 * (width / 8), button_y, button_width, button_height)
            hover_o = playOButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, playOButton, "Play as O", smallFont, blue, shadow, white, hover=hover_o)

            click, _, _ = pygame.mouse.get_pressed()
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if playXButton.collidepoint(mouse):
                    time.sleep(0.2)
                    user = ttt.X
                elif playOButton.collidepoint(mouse):
                    time.sleep(0.2)
                    user = ttt.O

    else:
        grid_size = 4
        available_space = min(width * 0.8, height * 0.7) 
        tile_size = available_space / grid_size
        
        board_width = tile_size * grid_size
        board_height = tile_size * grid_size
        board_left = (width - board_width) / 2
        board_top = (height - board_height) / 2 + height * 0.05 
        
        tile_origin = (board_left, board_top)
        
        tiles = []
        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                rect = pygame.Rect(tile_origin[0] + j * tile_size, tile_origin[1] + i * tile_size, 
                                 tile_size, tile_size)
                
                pygame.draw.rect(screen, black, rect)
                pygame.draw.rect(screen, white, rect, 3)
                
                inner_shadow = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6)
                pygame.draw.rect(screen, (30, 30, 30), inner_shadow, 1)

                if board[i][j] != ttt.EMPTY:
                    draw_move(screen, rect, board[i][j])
                    
                row.append(rect)
            tiles.append(row)

        game_over = ttt.terminal(board)
        player = ttt.player(board)

        panel_height = height * 0.15
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, width, panel_height))
        pygame.draw.line(screen, white, (0, panel_height), (width, panel_height), 2)
        
        if game_over and winning_line is None:
            winner_symbol = ttt.winner(board)
            winning_line = get_winning_line(board)
            if winner_symbol == user:
                winner_player = "You"
            elif winner_symbol is not None:
                winner_player = "Computer"
            else:
                winner_player = None  
        
        if game_over:
            if winner_player is None:
                title = f"Game Over: Tie!"
            else:
                title = f"Game Over: {winner_player} win!"
        elif user == player:
            title = f"Your Turn (Playing as {user})"
        else:
            title = f"Computer Thinking..."
            
        title = mediumFont.render(title, True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), panel_height / 2 - 10)
        screen.blit(title, titleRect)
        
        diffText = smallFont.render(f"Difficulty: {difficulty.capitalize()}", True, white)
        diffRect = diffText.get_rect()
        diffRect.center = ((width / 2), panel_height - 20)
        screen.blit(diffText, diffRect)

        if winning_line is not None:
            if animation_progress < 1:
                animation_progress += 0.05  
            draw_winning_line(screen, winning_line[0], winning_line[1], tiles, animation_progress)

        if user != player and not game_over:
            if ai_turn:
                time.sleep(0.5)
                move = ttt.minimax(board, difficulty)
                board = ttt.result(board, move)
                ai_turn = False
            else:
                ai_turn = True

        click, _, _ = pygame.mouse.get_pressed()
        if click == 1 and user == player and not game_over:
            mouse = pygame.mouse.get_pos()
            for i in range(grid_size):
                for j in range(grid_size):
                    if (board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(mouse)):
                        board = ttt.result(board, (i, j))

        if game_over:
            panel_bottom_height = height * 0.15
            pygame.draw.rect(screen, (50, 50, 50), 
                           (0, height - panel_bottom_height, width, panel_bottom_height))
            pygame.draw.line(screen, white, 
                           (0, height - panel_bottom_height), 
                           (width, height - panel_bottom_height), 2)
            
            button_width = width / 4
            button_height = height * 0.08
            button_y = height - panel_bottom_height / 2 - button_height / 2
            
            againButton = pygame.Rect(width / 5, button_y, button_width, button_height)
            hover_retry = againButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, againButton, "Retry", smallFont, white, shadow, black, hover=hover_retry)

            quitButton = pygame.Rect(3 * (width / 5), button_y, button_width, button_height)
            hover_quit = quitButton.collidepoint(pygame.mouse.get_pos())
            draw_3d_button(screen, quitButton, "Quit", smallFont, white, shadow, black, hover=hover_quit)

            click, _, _ = pygame.mouse.get_pressed()
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if againButton.collidepoint(mouse):
                    time.sleep(0.2)
                    user = None
                    difficulty = None  
                    board = ttt.initial_state()
                    ai_turn = False
                    animation_progress = 0
                    winning_line = None
                    winner_player = None
                elif quitButton.collidepoint(mouse):
                    pygame.quit()
                    sys.exit()

    pygame.display.flip()
    clock.tick(60)  