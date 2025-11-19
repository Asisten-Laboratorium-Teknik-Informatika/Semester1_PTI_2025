import pygame
import chess
import os

# Initialize pygame
pygame.init()

# Folder path 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")

# Constants
BOARD_WIDTH = BOARD_HEIGHT = 800
SIDE_PANEL_WIDTH = 300
WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH
HEIGHT = BOARD_HEIGHT
SQ_SIZE = BOARD_WIDTH // 8

# Colors
LP = (245, 222, 179)
PINK = (255, 192, 203)
HIGHLIGHT = (255, 105, 180)
MOVE_COLOR = (100, 255, 100)
ATTACK_COLOR = (255, 80, 80)
LAST_MOVE_COLOR = (173, 216, 230)
PANEL_BG = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
PROMO_BG = (240, 240, 240)
PROMO_BORDER = (50, 50, 50)

# Fonts
pygame.font.init()
FONT_TITLE = pygame.font.SysFont("arial", 26, bold=True)
FONT_TEXT = pygame.font.SysFont("consolas", 22)
FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_PROMO = pygame.font.SysFont("arial", 28, bold=True)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chess")

# Load images
pieces = {}
for piece in ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',
              'bp', 'bn', 'bb', 'br', 'bq', 'bk']:
    img_path = os.path.join(IMG_DIR, f"{piece}.png")
    pieces[piece] = pygame.transform.scale(pygame.image.load(img_path), (SQ_SIZE, SQ_SIZE))

# Chess board
board = chess.Board()

# Game state trackers
move_history = []     
captured_white = []
captured_black = []


# --- Draw Functions ---
def draw_board():
    for row in range(8):
        for col in range(8):
            color = LP if (row + col) % 2 == 0 else PINK
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces():
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece:
                prefix = 'w' if piece.color == chess.WHITE else 'b'
                key = prefix + piece.symbol().lower()
                if key in pieces:
                    screen.blit(pieces[key], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_highlights():
    if last_move:
        for sq in [last_move.from_square, last_move.to_square]:
            col = chess.square_file(sq)
            row = 7 - chess.square_rank(sq)
            pygame.draw.rect(screen, LAST_MOVE_COLOR, (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    if selected_square is not None:
        col = chess.square_file(selected_square)
        row = 7 - chess.square_rank(selected_square)
        pygame.draw.rect(screen, HIGHLIGHT, (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)


def draw_move_dots():
    for move in legal_moves:
        target = move.to_square
        col = chess.square_file(target)
        row = 7 - chess.square_rank(target)
        target_piece = board.piece_at(target)
        color = ATTACK_COLOR if target_piece else MOVE_COLOR
        center = (col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2)
        radius = 15 if not target_piece else 20
        pygame.draw.circle(screen, color, center, radius)


def draw_side_panel():
    pygame.draw.rect(screen, PANEL_BG, (BOARD_WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT))

    # Title
    title = FONT_TITLE.render("Game Info", True, TEXT_COLOR)
    screen.blit(title, (BOARD_WIDTH + 60, 20))

    # Whose turn
    turn_text = "White" if board.turn == chess.WHITE else "Pink"
    turn_surface = FONT_TEXT.render(f"Turn: {turn_text}", True, TEXT_COLOR)
    screen.blit(turn_surface, (BOARD_WIDTH + 20, 70))

    # Move count
    move_count_surface = FONT_TEXT.render(f"Move #: {board.fullmove_number}", True, TEXT_COLOR)
    screen.blit(move_count_surface, (BOARD_WIDTH + 20, 100))

    # Divider
    pygame.draw.line(screen, (180, 180, 180), (BOARD_WIDTH + 10, 130),
                     (BOARD_WIDTH + SIDE_PANEL_WIDTH - 10, 130), 2)

    # Captured pieces section
    y_pos = 150
    cap_title = FONT_TEXT.render("Captured Pieces:", True, TEXT_COLOR)
    screen.blit(cap_title, (BOARD_WIDTH + 20, y_pos))
    y_pos += 30

    # Captured by White (black pieces)
    white_cap_title = FONT_SMALL.render("White captured:", True, (200, 200, 200))
    screen.blit(white_cap_title, (BOARD_WIDTH + 20, y_pos))
    y_pos += 20
    x_pos = BOARD_WIDTH + 10
    for p in captured_white:
        key = 'b' + p.lower()
        if key in pieces:
            screen.blit(pygame.transform.scale(pieces[key], (40, 40)), (x_pos, y_pos))
            x_pos += 10
    y_pos += 40

    # Captured by Pink (white pieces)
    black_cap_title = FONT_SMALL.render("Pink captured:", True, (200, 200, 200))
    screen.blit(black_cap_title, (BOARD_WIDTH + 20, y_pos))
    y_pos += 20
    x_pos = BOARD_WIDTH + 10
    for p in captured_black:
        key = 'w' + p.lower()
        if key in pieces:
            screen.blit(pygame.transform.scale(pieces[key], (40, 40)), (x_pos, y_pos))
            x_pos += 10
    y_pos += 50

    # Divider
    pygame.draw.line(screen, (180, 180, 180), (BOARD_WIDTH + 10, y_pos),
                     (BOARD_WIDTH + SIDE_PANEL_WIDTH - 10, y_pos), 2)
    y_pos += 10

    # Move history
    history_title = FONT_TEXT.render("Move History:", True, TEXT_COLOR)
    screen.blit(history_title, (BOARD_WIDTH + 20, y_pos))
    y_pos += 30

    # Display last few moves
    moves_to_show = move_history[-12:]  # show up to 10 last half-moves
    for i, m in enumerate(moves_to_show):
        move_surface = FONT_SMALL.render(m, True, (220, 220, 220))
        screen.blit(move_surface, (BOARD_WIDTH + 25, y_pos + i * 20))


def draw_promotion_box():
    """Overlay box to choose promotion piece."""
    overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    box_w, box_h = 300, 200
    box_x = (BOARD_WIDTH - box_w) // 2
    box_y = (BOARD_HEIGHT - box_h) // 2
    pygame.draw.rect(screen, PROMO_BG, (box_x, box_y, box_w, box_h))
    pygame.draw.rect(screen, PROMO_BORDER, (box_x, box_y, box_w, box_h), 3)
    text = FONT_PROMO.render("Promote to:", True, (0, 0, 0))
    screen.blit(text, (box_x + 70, box_y + 20))
    choices = [('Q', chess.QUEEN), ('R', chess.ROOK), ('B', chess.BISHOP), ('N', chess.KNIGHT)]
    for i, (label, _) in enumerate(choices):
        option_rect = pygame.Rect(box_x + 35 + i * 60, box_y + 80, 50, 50)
        pygame.draw.rect(screen, (200, 200, 200), option_rect)
        pygame.draw.rect(screen, PROMO_BORDER, option_rect, 2)
        txt = FONT_PROMO.render(label, True, (0, 0, 0))
        screen.blit(txt, (option_rect.x + 12, option_rect.y + 5))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for i, (_, piece_type) in enumerate(choices):
                    rect = pygame.Rect(box_x + 35 + i * 60, box_y + 80, 50, 50)
                    if rect.collidepoint(x, y):
                        return piece_type


# --- Game Loop ---
running = True
selected_square = None
legal_moves = []
last_move = None

while running:
    draw_board()
    draw_highlights()
    draw_pieces()
    draw_move_dots()
    draw_side_panel()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if x > BOARD_WIDTH:
                continue
            col, row = x // SQ_SIZE, 7 - (y // SQ_SIZE)
            square = chess.square(col, row)

            if selected_square is None:
                if board.piece_at(square) and board.piece_at(square).color == board.turn:
                    selected_square = square
                    legal_moves = [m for m in board.legal_moves if m.from_square == square]
            else:
                move = chess.Move(selected_square, square)
                piece = board.piece_at(selected_square)
                captured_piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN:
                    target_rank = chess.square_rank(square)
                    if (piece.color == chess.WHITE and target_rank == 7) or \
                       (piece.color == chess.BLACK and target_rank == 0):
                        promotion_piece = draw_promotion_box()
                        move = chess.Move(selected_square, square, promotion=promotion_piece)

                if move in board.legal_moves:
                    # Track captured piece
                    if captured_piece:
                        if piece.color == chess.WHITE:
                            captured_white.append(captured_piece.symbol())
                        else:
                            captured_black.append(captured_piece.symbol())

                    san = board.san(move)  
                    board.push(move)
                    last_move = move
                    move_history.append(san)


                selected_square = None
                legal_moves = []

pygame.quit()
