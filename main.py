import pygame
import sys
import time
import gamelogic as ttt
import random

pygame.init()

display_info = pygame.display.Info()
screen_width = min(display_info.current_w - 100, 1024)
screen_height = min(display_info.current_h - 100, 768)
size = width, height = screen_width, screen_height

# --- Colors (updated for vibrancy and contrast) ---
background_top = (10, 10, 70)         # Deep vivid blue
background_bottom = (0, 220, 255)     # Bright cyan

panel_color = (30, 30, 90)            # Dark royal blue
tile_border_color = (255, 165, 0)    # Bright orange border
tile_inner_shadow = (255, 215, 0)    # Gold highlight inside tiles

text_color = (255, 255, 255)          # Pure white text
highlight_color = (255, 69, 0)        # Vibrant orange-red highlight
button_base = (0, 140, 255)            # Bright blue buttons
button_text = (255, 255, 255)          # White button text
button_hover = (0, 200, 255)           # Lighter blue on hover

win_line_color = (255, 255, 0)         # Bright yellow winning line

triangle_color = (255, 69, 0)          # Orange-red triangle (user shape)
diamond_color = (0, 255, 255)          # Bright cyan diamond (AI shape)


screen = pygame.display.set_mode(size)
pygame.display.set_caption("Tic-Tac-Toe Modern Vibrant")

small_font_size = int(height * 0.035)
medium_font_size = int(height * 0.06)

smallFont = pygame.font.SysFont("Segoe UI", small_font_size)
mediumFont = pygame.font.SysFont("Segoe UI", medium_font_size)

# User/game state variables
user_name = ""
input_active = True
input_rect = pygame.Rect(width / 2 - 180, height * 0.35, 360, 50)

difficulty = None
user = ttt.X
ai = ttt.O
player_shape_triangle = True

board = ttt.initial_state()
ai_turn = False
animation_progress = 0
winning_line = None
winner_player = None

player_wins = 0
ai_wins = 0
ties = 0

cursor_visible = True
cursor_timer = 0

settings_open = False

clock = pygame.time.Clock()

def draw_particles(surface):
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(1, 3)
        alpha = random.randint(50, 150)
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (radius, radius), radius)
        surface.blit(surf, (x, y))

def draw_rounded_rect(surface, rect, color, radius=15):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_shadow(surface, rect, radius=15, offset=(5,5), shadow_color=(0,0,0,80)):
    shadow_surf = pygame.Surface((rect.width + offset[0]*2, rect.height + offset[1]*2), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=radius)
    surface.blit(shadow_surf, (rect.x - offset[0], rect.y - offset[1]))

def draw_button(surface, rect, text, font, base_color, hover, active):
    shadow_col = (0,0,0,120) if not active else (0,0,0,180)
    draw_shadow(surface, rect, radius=rect.height//2, offset=(4,4), shadow_color=shadow_col)

    color = tuple(min(c + 50, 255) for c in base_color) if hover else base_color
    draw_rounded_rect(surface, rect, color, radius=rect.height//2)

    text_surf = font.render(text, True, (0,0,0,150))
    text_rect = text_surf.get_rect(center=(rect.centerx + 1, rect.centery + 1))
    surface.blit(text_surf, text_rect)

    text_surf = font.render(text, True, button_text)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

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
        start_pos = (tiles[index][0].left + 12, tiles[index][0].centery)
        end_pos = (tiles[index][3].right - 12, tiles[index][3].centery)
        current_end = (start_pos[0] + (end_pos[0] - start_pos[0]) * min(progress, 1.0), start_pos[1])
    elif line_type == "column":
        start_pos = (tiles[0][index].centerx, tiles[0][index].top + 12)
        end_pos = (tiles[3][index].centerx, tiles[3][index].bottom - 12)
        current_end = (start_pos[0], start_pos[1] + (end_pos[1] - start_pos[1]) * min(progress, 1.0))
    elif line_type == "diagonal":
        start_pos = (tiles[0][0].left + 12, tiles[0][0].top + 12)
        end_pos = (tiles[3][3].right - 12, tiles[3][3].bottom - 12)
        current_end = (start_pos[0] + (end_pos[0] - start_pos[0]) * min(progress, 1.0),
                      start_pos[1] + (end_pos[1] - start_pos[1]) * min(progress, 1.0))
    elif line_type == "anti-diagonal":
        start_pos = (tiles[0][3].right - 12, tiles[0][3].top + 12)
        end_pos = (tiles[3][0].left + 12, tiles[3][0].bottom - 12)
        current_end = (start_pos[0] + (end_pos[0] - start_pos[0]) * min(progress, 1.0),
                      start_pos[1] + (end_pos[1] - start_pos[1]) * min(progress, 1.0))
    line_width = int(height * 0.009)
    pygame.draw.line(surface, win_line_color, start_pos, current_end, line_width)

def draw_triangle(surface, rect, color):
    cx, cy = rect.center
    size = rect.width * 0.5
    points = [
        (cx, cy - size / 1.5),
        (cx - size / 1.5, cy + size / 1.5),
        (cx + size / 1.5, cy + size / 1.5),
    ]
    pygame.draw.polygon(surface, color, points)

def draw_diamond(surface, rect, color):
    cx, cy = rect.center
    size = rect.width * 0.5
    points = [
        (cx, cy - size / 1.5),
        (cx - size / 1.5, cy),
        (cx, cy + size / 1.5),
        (cx + size / 1.5, cy),
    ]
    pygame.draw.polygon(surface, color, points)

def draw_move(surface, rect, move):
    if move == user:
        draw_triangle(surface, rect, triangle_color)
    else:
        draw_diamond(surface, rect, diamond_color)

def draw_scorecard(surface, player_name, player_wins, ai_wins, ties):
    padding = 15
    rect_height = height * 0.1
    rect = pygame.Rect(padding, padding, width - 2 * padding, rect_height)
    draw_shadow(surface, rect, radius=20, offset=(6, 6), shadow_color=(0, 0, 0, 40))
    draw_rounded_rect(surface, rect, panel_color, radius=20)
    pygame.draw.rect(surface, highlight_color, rect, 3, border_radius=20)

    def draw_shadowed_text(text, pos):
        shadow_surf = smallFont.render(text, True, (0,0,0,160))
        surface.blit(shadow_surf, (pos[0]+1, pos[1]+1))
        text_surf = smallFont.render(text, True, text_color)
        surface.blit(text_surf, pos)

    gap = (width - 2 * padding) // 3
    draw_shadowed_text(f"{player_name}'s Wins: {player_wins}", (padding + 20, padding + rect_height // 3))
    draw_shadowed_text(f"AI Wins: {ai_wins}", (padding + gap + 20, padding + rect_height // 3))
    draw_shadowed_text(f"Ties: {ties}", (padding + 2 * gap + 20, padding + rect_height // 3))

def truncate_text(font, text, max_width):
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    max_len = len(text)
    while max_len > 0:
        candidate = text[:max_len] + ellipsis
        if font.size(candidate)[0] <= max_width:
            return candidate
        max_len -= 1
    return ellipsis

# --- Main loop ---
while True:
    dt = clock.tick(60) / 1000
    cursor_timer += dt
    if cursor_timer >= 0.5:
        cursor_timer = 0
        cursor_visible = not cursor_visible

    click, _, _ = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                user_name = user_name[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if len(user_name.strip()) > 0:
                    input_active = False
            else:
                if len(user_name) < 20 and event.unicode.isprintable():
                    user_name += event.unicode

        if not input_active and event.type == pygame.MOUSEBUTTONDOWN:
            if settings_open:
                tri_btn = pygame.Rect(width/2 - 220, height*0.6, 180, 50)
                dia_btn = pygame.Rect(width/2 + 40, height*0.6, 180, 50)
                if tri_btn.collidepoint(mouse_pos):
                    player_shape_triangle = True
                    user = ttt.X
                    ai = ttt.O
                    settings_open = False
                elif dia_btn.collidepoint(mouse_pos):
                    player_shape_triangle = False
                    user = ttt.O
                    ai = ttt.X
                    settings_open = False

    # --- Draw Background ---
    for y in range(height):
        ratio = y / height
        r = int(background_top[0]*(1-ratio) + background_bottom[0]*ratio)
        g = int(background_top[1]*(1-ratio) + background_bottom[1]*ratio)
        b = int(background_top[2]*(1-ratio) + background_bottom[2]*ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    draw_particles(screen)

    display_name = user_name if user_name else "Player"
    max_score_name_width = width - 160
    display_name = truncate_text(smallFont, display_name, max_score_name_width)
    draw_scorecard(screen, display_name, player_wins, ai_wins, ties)

    # --- UI States ---
    if input_active:
        prompt = mediumFont.render("Enter your name:", True, text_color)
        prompt_rect = prompt.get_rect(center=(width/2, height*0.25))
        screen.blit(prompt, prompt_rect)

        pygame.draw.rect(screen, panel_color, input_rect, border_radius=12)
        pygame.draw.rect(screen, button_hover if input_active else button_base, input_rect, 3, border_radius=12)

        max_text_width = input_rect.width - 20
        displayed_text = user_name
        while mediumFont.size(displayed_text)[0] > max_text_width and len(displayed_text) > 0:
            displayed_text = displayed_text[1:]

        txt_surface = mediumFont.render(displayed_text, True, text_color)
        screen.blit(txt_surface, (input_rect.x + 10, input_rect.y + (input_rect.height - txt_surface.get_height())//2))

        if cursor_visible:
            cursor_x = input_rect.x + 10 + txt_surface.get_width() + 1
            cursor_y = input_rect.y + 12
            cursor_h = txt_surface.get_height() - 10
            if cursor_x + 2 <= input_rect.x + input_rect.width - 4:
                pygame.draw.rect(screen, text_color, (cursor_x, cursor_y, 2, cursor_h))

    elif settings_open:
        header = mediumFont.render("Choose your shape:", True, text_color)
        header_rect = header.get_rect(center=(width/2, height*0.5))
        screen.blit(header, header_rect)

        tri_btn = pygame.Rect(width/2 - 220, height*0.6, 180, 50)
        dia_btn = pygame.Rect(width/2 + 40, height*0.6, 180, 50)

        draw_button(screen, tri_btn, "Triangle ▲", mediumFont, triangle_color, tri_btn.collidepoint(mouse_pos), player_shape_triangle)
        draw_button(screen, dia_btn, "Diamond ◆", mediumFont, diamond_color, dia_btn.collidepoint(mouse_pos), not player_shape_triangle)

    else:
        if difficulty is None:
            prompt = mediumFont.render(f"Welcome {user_name}, select challenge level:", True, text_color)
            prompt_rect = prompt.get_rect(center=(width/2, height*0.25))
            screen.blit(prompt, prompt_rect)

            button_width = width / 5
            button_height = height * 0.07
            button_y = height * 0.42

            level1Button = pygame.Rect(width / 6, button_y, button_width, button_height)
            level2Button = pygame.Rect(width / 2 - button_width / 2, button_y, button_width, button_height)
            level3Button = pygame.Rect(width - width / 6 - button_width, button_y, button_width, button_height)
            settingsButton = pygame.Rect(width / 2 - 90, button_y + button_height + 20, 180, 38)

            hover_level1 = level1Button.collidepoint(mouse_pos)
            hover_level2 = level2Button.collidepoint(mouse_pos)
            hover_level3 = level3Button.collidepoint(mouse_pos)
            hover_settings = settingsButton.collidepoint(mouse_pos)

            draw_button(screen, level1Button, "Level 1", mediumFont, button_base, hover_level1, False)
            draw_button(screen, level2Button, "Level 2", mediumFont, button_base, hover_level2, False)
            draw_button(screen, level3Button, "Level 3", mediumFont, button_base, hover_level3, False)
            draw_button(screen, settingsButton, "Change Shape", smallFont, button_base, hover_settings, False)

            if click == 1:
                if level1Button.collidepoint(mouse_pos):
                    time.sleep(0.25)
                    difficulty = "easy"
                elif level2Button.collidepoint(mouse_pos):
                    time.sleep(0.25)
                    difficulty = "medium"
                elif level3Button.collidepoint(mouse_pos):
                    time.sleep(0.25)
                    difficulty = "hard"
                elif settingsButton.collidepoint(mouse_pos):
                    settings_open = True

        else:
            # Game board + shape select buttons + logic
            if not settings_open:
                diff_text = smallFont.render(f"Challenge Level: {difficulty.capitalize()}", True, text_color)
                diff_rect = diff_text.get_rect(center=(width/2, height*0.4))
                screen.blit(diff_text, diff_rect)

                button_width = width / 4
                button_height = height * 0.07
                button_y = height * 0.5

                playTriangleButton = pygame.Rect(width / 8, button_y, button_width, button_height)
                playDiamondButton = pygame.Rect(5 * width / 8, button_y, button_width, button_height)

                hover_t = playTriangleButton.collidepoint(mouse_pos)
                hover_d = playDiamondButton.collidepoint(mouse_pos)

                if click == 1:
                    if playTriangleButton.collidepoint(mouse_pos):
                        time.sleep(0.25)
                        user = ttt.X
                        ai = ttt.O
                        player_shape_triangle = True
                    elif playDiamondButton.collidepoint(mouse_pos):
                        time.sleep(0.25)
                        user = ttt.O
                        ai = ttt.X
                        player_shape_triangle = False

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

                        grad_surf = pygame.Surface((rect.width, rect.height))
                        for y in range(rect.height):
                            grad = int(255 - (y / rect.height) * 20)
                            pygame.draw.line(grad_surf, (grad, grad, grad), (0, y), (rect.width, y))
                        grad_surf.set_alpha(230)
                        screen.blit(grad_surf, rect.topleft)

                        pygame.draw.rect(screen, tile_border_color, rect, 3, border_radius=12)
                        inner_shadow = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8)
                        pygame.draw.rect(screen, tile_inner_shadow, inner_shadow, 2, border_radius=12)

                        if board[i][j] != ttt.EMPTY:
                            draw_move(screen, rect, board[i][j])

                        row.append(rect)
                    tiles.append(row)

                game_over = ttt.terminal(board)
                player_turn = ttt.player(board)

                panel_height = height * 0.15
                panel_rect = pygame.Rect(0, 0, width, panel_height)
                draw_shadow(screen, panel_rect, radius=15, offset=(5, 5), shadow_color=(0, 0, 0, 70))
                draw_rounded_rect(screen, panel_rect, panel_color, radius=15)
                pygame.draw.line(screen, tile_border_color, (0, panel_height), (width, panel_height), 2)

                if game_over and winning_line is None:
                    winner_symbol = ttt.winner(board)
                    winning_line = get_winning_line(board)
                    if winner_symbol == user:
                        winner_player = user_name
                        player_wins += 1
                    elif winner_symbol is not None:
                        winner_player = "AI"
                        ai_wins += 1
                    else:
                        winner_player = None
                        ties += 1

                if game_over:
                    status_text = "It's a Tie!" if winner_player is None else f"{winner_player} Wins!"
                elif user == player_turn:
                    status_text = f"{user_name}, it's your move!"
                else:
                    status_text = "AI is thinking..."

                status_shadow = mediumFont.render(status_text, True, (0, 0, 0, 150))
                status_rect = status_shadow.get_rect(center=(width / 2 + 2, panel_height / 2 - 8))
                screen.blit(status_shadow, status_rect)

                status_render = mediumFont.render(status_text, True, text_color)
                status_rect = status_render.get_rect(center=(width / 2, panel_height / 2 - 10))
                screen.blit(status_render, status_rect)

                diff_text = smallFont.render(f"Challenge Level: {difficulty.capitalize()}", True, text_color)
                diff_rect = diff_text.get_rect(center=(width / 2, panel_height - 20))
                screen.blit(diff_text, diff_rect)

                if winning_line is not None:
                    if animation_progress < 1:
                        animation_progress += 0.05
                    draw_winning_line(screen, winning_line[0], winning_line[1], tiles, animation_progress)

                # AI Move logic: AI acts only when it's AI's turn, game not over, and delay is over
                if user != player_turn and not game_over:
                    if ai_turn:
                        # Small delay for AI thinking
                        time.sleep(0.5)
                        move = ttt.minimax(board, difficulty, maximizing_player=ai)
                        if move is not None:
                            board = ttt.result(board, move)
                        ai_turn = False
                    else:
                        ai_turn = True

                if click == 1 and user == player_turn and not game_over:
                    mouse = pygame.mouse.get_pos()
                    for i in range(grid_size):
                        for j in range(grid_size):
                            if board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(mouse):
                                board = ttt.result(board, (i, j))
                                # Reset AI turn to allow AI to move next
                                ai_turn = False

                if game_over:
                    panel_bottom_height = height * 0.15
                    panel_bottom_rect = pygame.Rect(0, height - panel_bottom_height, width, panel_bottom_height)
                    draw_shadow(screen, panel_bottom_rect, radius=15, offset=(5, 5), shadow_color=(0, 0, 0, 70))
                    draw_rounded_rect(screen, panel_bottom_rect, panel_color, radius=15)
                    pygame.draw.line(screen, tile_border_color, (0, height - panel_bottom_height), (width, height - panel_bottom_height), 2)

                    button_width = width / 4
                    button_height = height * 0.07
                    button_y = height - panel_bottom_height / 2 - button_height / 2

                    againButton = pygame.Rect(width / 5, button_y, button_width, button_height)
                    hover_retry = againButton.collidepoint(mouse_pos)
                    draw_button(screen, againButton, "Play Again", mediumFont, button_base, hover_retry, False)

                    quitButton = pygame.Rect(3 * (width / 5), button_y, button_width, button_height)
                    hover_quit = quitButton.collidepoint(mouse_pos)
                    draw_button(screen, quitButton, "Exit", mediumFont, button_base, hover_quit, False)

                    if click == 1:
                        if againButton.collidepoint(mouse_pos):
                            time.sleep(0.25)
                            user_name = ""
                            input_active = True
                            difficulty = None
                            board = ttt.initial_state()
                            ai_turn = False
                            animation_progress = 0
                            winning_line = None
                            winner_player = None
                            settings_open = False
                        elif quitButton.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()

    pygame.display.flip()
