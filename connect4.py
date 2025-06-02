import numpy as np
import pygame
import sys
import math
import random

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
WHITE = (255,255,255)

ROW_COUNT = 6
COLUMN_COUNT = 7

# Special piece types
NORMAL = 0
TIME_BOMB = 1
RAINBOW = 2

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece, piece_type=NORMAL):
	if piece_type == TIME_BOMB:
		# Clear 3x3 area around the drop point
		for r in range(max(0, row-1), min(ROW_COUNT, row+2)):
			for c in range(max(0, col-1), min(COLUMN_COUNT, col+2)):
				board[r][c] = 0
	elif piece_type == RAINBOW:
		# Can be placed anywhere
		board[row][col] = piece
	else:
		board[row][col] = piece

def remove_piece(board, row, col):
	board[row][col] = 0

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def get_top_piece(board, col):
	for r in range(ROW_COUNT-1, -1, -1):
		if board[r][col] != 0:
			return r
	return None

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == 1:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == 2: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()


board = create_board()
print_board(board)
game_over = False
turn = 0
power_shot_used = [False, False]
scores = [0, 0]  # Track scores for each player
special_pieces = [True, True]  # Track if players have special pieces available
special_type = [NORMAL, NORMAL]  # Track which special piece is selected

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)
smallfont = pygame.font.SysFont("monospace", 25)

def draw_status():
	pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
	# Draw scores
	score_text = f"P1: {scores[0]}  P2: {scores[1]}"
	score_label = smallfont.render(score_text, 1, WHITE)
	screen.blit(score_label, (width//2 - 50, 10))
	
	# Draw power shot status
	power_shot_text = f"Power Shot: {'Used' if power_shot_used[turn] else 'Available'}"
	power_label = smallfont.render(power_shot_text, 1, GREEN)
	screen.blit(power_label, (10, 10))
	
	# Draw special piece status
	special_text = f"Special: {'Time Bomb' if special_type[turn] == TIME_BOMB else 'Rainbow' if special_type[turn] == RAINBOW else 'None'}"
	special_label = smallfont.render(special_text, 1, ORANGE)
	screen.blit(special_label, (width - 200, 10))

while not game_over:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_t and special_pieces[turn]:  # 'T' for Time Bomb
				special_type[turn] = TIME_BOMB
			elif event.key == pygame.K_r and special_pieces[turn]:  # 'R' for Rainbow
				special_type[turn] = RAINBOW
			draw_status()

		if event.type == pygame.MOUSEMOTION:
			draw_status()
			posx = event.pos[0]
			if turn == 0:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
			else: 
				pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			draw_status()
			posx = event.pos[0]
			col = int(math.floor(posx/SQUARESIZE))

			# Check if right mouse button is pressed for power shot
			if event.button == 3 and not power_shot_used[turn]:
				row = get_top_piece(board, col)
				if row is not None and board[row][col] != turn + 1:
					remove_piece(board, row, col)
					power_shot_used[turn] = True
					draw_board(board)
					continue

			# Normal move or special piece
			if is_valid_location(board, col):
				row = get_next_open_row(board, col)
				if special_pieces[turn] and special_type[turn] != NORMAL:
					drop_piece(board, row, col, turn + 1, special_type[turn])
					special_pieces[turn] = False
					special_type[turn] = NORMAL
				else:
					drop_piece(board, row, col, turn + 1)

				if winning_move(board, turn + 1):
					scores[turn] += 1
					label = myfont.render(f"Player {turn + 1} wins!!", 1, RED if turn == 0 else YELLOW)
					screen.blit(label, (40,10))
					game_over = True
					# Reset for next game
					board = create_board()
					power_shot_used = [False, False]
					special_pieces = [True, True]  # Give special pieces for next game
					special_type = [NORMAL, NORMAL]

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

			if game_over:
				pygame.time.wait(3000)
				game_over = False  # Continue to next game