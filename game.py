from Color import Color
from TetrisBoard import TetrisBoard
import time, random

ratio = 40
class TetrisGame:
	def __init__(self):
		self.close_requested = False
		self.target_fps = 60
		self.window_size = (3 * 10 * ratio, 1 * 22 * ratio)
		self.title = "Tetris"
	def start(self):
		# Init
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		board = TetrisBoard(10, 22, *self.window_size, seed = random.seed(), ratio = ratio)
		lastUpdate = time.time()
		leftTime = 0
		rightTime = 0
		verTime = 0
		upTime = 0
		UPDATE_INTERVAL = 1
		HORIZONTAL_INTERVAL = 0.1
		DOWN_INTERVAL = 0.05
		ROTATIONAL_INTERVAL = 0.33

		up = False
		left = False
		right = False
		down = False
		# Main Game Loop
		while not self.close_requested:
			# Handles "X" button of window
			spiked = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.close_requested = True
				#press button
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						if(not up): #inital press
							upTime = time.time()
							board.rotateFallingPiece(1)#for tapping the button vs holding it
						up = True
					if event.key == pygame.K_LEFT:
						if(not left): #inital press
							leftTime = time.time()
							board.moveFallingPiece(moveX=-1, moveY=0)#for tapping the button vs holding it
						left = True
					if event.key == pygame.K_RIGHT:
						if(not right):#inital press
							rightTime = time.time()
							board.moveFallingPiece(moveX=1, moveY=0) #for tapping the button vs holding it
						right = True
					if event.key == pygame.K_DOWN:
						if(not down):#initial press
							verTime = time.time()
							board.moveFallingPiece(moveX=0, moveY=1)#for tapping the button vs holding it
						down = True
					if event.key == pygame.K_SPACE:
						board.spike()
						spiked = True
					#release button
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_UP:
						up = False
					if event.key == pygame.K_LEFT:
						left = False
					if event.key == pygame.K_RIGHT:
						right = False
					if event.key == pygame.K_DOWN:
						down = False
			#execute hold
			if(up):
				if upTime + ROTATIONAL_INTERVAL < time.time():#rotates every 1/3 second
					board.rotateFallingPiece(1)
					upTime += ROTATIONAL_INTERVAL
			if(left):
				if leftTime + HORIZONTAL_INTERVAL < time.time():#moves left every .1 seconds
					board.moveFallingPiece(moveX=-1, moveY=0)
					leftTime += HORIZONTAL_INTERVAL
			if(right):
				if rightTime + HORIZONTAL_INTERVAL < time.time():#mvoes right every .1 seconds
					board.moveFallingPiece(moveX=1, moveY=0)
					rightTime += HORIZONTAL_INTERVAL
			if(down):
				if verTime + DOWN_INTERVAL < time.time():#moves down every .01 seconds
					board.moveFallingPiece(moveX=0, moveY=1)
					verTime += DOWN_INTERVAL
			# Updates the game
			lose = False
			if lastUpdate + UPDATE_INTERVAL < time.time():
				if(not spiked):
					if(not board.update()):
						lose = True
					else:
						lastUpdate += UPDATE_INTERVAL
				else:
					lastUpdate += UPDATE_INTERVAL
			# Check for lose
			if lose:
				board.lose(self.screen, self.window_size)
			else:
				#Draw the Board
				self.screen.fill((255,239,213))
				board.render(self.screen, * self.window_size, shiftx = self.window_size[0]/3)
				board.showScore(self.screen, self.window_size)
				board.showLevel(self.screen, self.window_size)
				#levelcheck
				if(board.linesCleared >= board.level * 10):
					board.level += 1
			#pygame.draw.rect(self.screen, Color.BLACK, [x, y, width, height], 0)

			pygame.display.flip()
			self.clock.tick(self.target_fps)



import pygame
pygame.init()
game = TetrisGame()
game.start()
pygame.quit()
