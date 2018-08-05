import numpy as np
from TetrisConstants import *
import pygame
from Color import Color

class TetrisBoard:
	def __init__(self, width, height, seed):
		self.random = np.random.RandomState(seed) # Initialize random with seed
		self.width = width
		self.height = height
		self.grid = self.createBlankGrid()
		self.startX = int(width / 2 - TetrisConstants.TEMPLATE_WIDTH / 2)
		self.startY =  0
		self.fallingPiece = self.getRandomNewPiece()
		self.nextPiece = self.getRandomNewPiece()
		self.score = 0
		self.level = 1
		self.linesCleared = 0
	def createBlankGrid(self):
		grid = np.empty((self.width, self.height), dtype=str) # 1 char string
		grid[:] = BLANK
		return grid
	# Does not include falling piece
	def isBlankLine(self, y):
		return np.all(self.grid[:, y] == BLANK)
	# Does not include falling piece
	def lowestBlankLine(self):
		for y in range(self.height - 1, -1, -1):
			if self.isBlankLine(y):
				return y
		return self.height
	def isCompleteLine(self, grid, y):
		return np.all(grid[:, y] != BLANK)
	def removeCompletedLines(self):
		numLinesRemoved = 0
		for y in range(0, self.height): # Go from bottom up
			if self.isCompleteLine(self.grid, y):
				self.grid[:, 1 : y + 1] = self.grid[:, :y]
				self.grid[:, 0] = BLANK
				numLinesRemoved += 1
		#scoring
		self.changeScore(numLinesRemoved)
		self.linesCleared += numLinesRemoved
	def isOnBoard(self, x, y):
		return x >= 0 and x < self.width and y >= 0 and y < self.height
	def isValidPosition(self, piece, adjustX=0, adjustY=0, rotation=None):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if self.getTemplate(piece, x, y, rotation) == BLANK:
					continue
				if not self.isOnBoard(piece.x + x + adjustX, piece.y + y + adjustY):
					return False
				if self.grid[piece.x + x + adjustX, piece.y + y + adjustY] != BLANK:
					return False
		return True
	def setPiece(self, piece):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not self.getTemplate(piece, x, y) == BLANK:
					self.grid[piece.x + x, piece.y + y] = self.getTemplate(piece, x, y)
	def getTemplate(self, piece, x=None, y=None, rotation=None):
		if x is None or y is None:
			return TetrisConstants.PIECES[piece.type].template[piece.rotation]
		elif rotation is None:
			return TetrisConstants.PIECES[piece.type].template[piece.rotation][x][y]
		else:
			return TetrisConstants.PIECES[piece.type].template[rotation][x][y]
	def getRandomNewPiece(self):
		pieceType = self.getRandomPieceType()
		return Piece(self.startX, self.startY, pieceType, self.getRandomRotation(pieceType))
	def getRandomPieceType(self):
		return self.random.choice(list(TetrisConstants.PIECES.keys()))
	def getRandomRotation(self, pieceType):
		return self.random.randint(0, len(TetrisConstants.PIECES[pieceType].template))
	def moveFallingPiece(self, moveX, moveY):
		if self.isValidPosition(self.fallingPiece, adjustX=moveX, adjustY=moveY):
			self.fallingPiece.x += moveX
			self.fallingPiece.y += moveY
			return True
		else:
			return False
	def spike(self):
		adjustY = 1
		while(self.isValidPosition(self.fallingPiece, adjustY = adjustY)):
			adjustY += 1
		self.moveFallingPiece(moveX = 0, moveY = adjustY - 1)
		if(not self.isValidPosition(self.nextPiece)):
			return False #loss condition
		self.setPiece(self.fallingPiece)
		self.removeCompletedLines()
		self.fallingPiece = self.nextPiece
		self.nextPiece = self.getRandomNewPiece()
	def rotateFallingPiece(self, rotate):
		numRotations = len(TetrisConstants.PIECES[self.fallingPiece.type].template)
		targetRotation = (((self.fallingPiece.rotation + rotate) % numRotations) + numRotations) % numRotations
		if self.isValidPosition(self.fallingPiece, rotation=targetRotation):
			self.fallingPiece.rotation = targetRotation
			return True
		else:
			return False
	def update(self): # Returns false if lose condition, true if normal condition
		if not self.isValidPosition(self.fallingPiece, adjustY=1):
			# falling piece has landed, set it on the board
			self.setPiece(self.fallingPiece)
			self.removeCompletedLines()
			# Check if anything is on top
			if(not self.isValidPosition(self.nextPiece)):
				return -1 # Loss condition
			self.fallingPiece = self.nextPiece
			self.nextPiece = self.getRandomNewPiece()
			return 1 # Signal that a piece was placed
		else:
			self.fallingPiece.y += 1
			return 0 # Normal condition
	def renderPiece(self, screen, piece, gridWidth, gridHeight, gridShiftX=0):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not self.getTemplate(piece, x, y) == BLANK:
					pygame.draw.rect(screen, self.border(TetrisConstants.PIECES[piece.type].color), [(piece.x + x) * gridWidth + gridShiftX, (piece.y + y) * gridHeight, gridWidth, gridHeight], 2)
					pygame.draw.rect(screen, TetrisConstants.PIECES[piece.type].color, [(piece.x + x) * gridWidth + gridShiftX + 1, (piece.y + y) * gridHeight + 1, gridWidth - 2, gridHeight - 2])
	def render(self, screen, renderWidth, renderHeight):
		gridWidth = renderWidth / (self.width)
		gridHeight = renderHeight / (self.height)
		gridWidth, gridHeight = min(gridWidth, gridHeight), min(gridWidth, gridHeight)
		gridShiftX = renderWidth / 2 - self.width / 2 * gridWidth
		# Render Grid
		pygame.draw.rect(screen, Color.BLACK, [gridShiftX, 0, gridWidth * self.width, gridHeight * self.height])
		for x in range(self.width):
			for y in range(self.height):
				if not self.grid[x, y] == BLANK:
					pygame.draw.rect(screen, self.border(TetrisConstants.PIECES[self.grid[x, y]].color), [x * gridWidth + gridShiftX, y * gridHeight, gridWidth, gridHeight], 2)
					pygame.draw.rect(screen, TetrisConstants.PIECES[self.grid[x, y]].color , [x * gridWidth + gridShiftX + 1, y * gridHeight + 1, gridWidth - 2, gridHeight - 2])
		# Render Falling Piece
		self.renderPiece(screen, self.fallingPiece, gridWidth, gridHeight, gridShiftX)
		# Render Next Piece
		#pygame.draw.rect(screen, (0, 130, 255), [self.ratio, self.ratio, gridWidth * 6, gridHeight * 6])
		self.renderPiece(screen, self.nextPiece, gridWidth, gridHeight, gridWidth)
	def changeScore(self, lines):
		if(lines == 1):
			score = 40
		elif(lines == 2):
			score = 100
		elif(lines == 3):
			score = 300
		elif(lines == 4):
			score = 1200
		else:
			score = 0
		self.score += self.level * score
	def lose(self, screen, size):
		basicfont = pygame.font.SysFont(None, 2 * self.ratio)
		text = basicfont.render('You lose!', True, Color.WHITE, Color.BLACK)
		textrect = text.get_rect(centerx = int(size[0]/2), centery = int(size[1]/2))
		screen.blit(text, textrect)
	def showScore(self, screen, size):
		basicfont = pygame.font.SysFont(None, self.ratio)
		text = basicfont.render("Score: " + str(self.score), True, Color.BLACK, (255,239,213))
		textrect = text.get_rect(topright = (size[0] - self.ratio * 2, self.ratio))
		screen.blit(text, textrect)
	def showLevel(self,screen,size):
		basicfont = pygame.font.SysFont(None, self.ratio)
		text = basicfont.render("Level: " + str(self.level), True, Color.BLACK, (255,239,213))
		textrect = text.get_rect(topright = (size[0] - self.ratio * 2, self.ratio * 2))
		screen.blit(text, textrect)
	#only for styling
	def border(self, color):
		arr = np.array(color, dtype = np.int)
		center = ((arr < 128) - .5) * 2
		return tuple(arr + center * 40)
