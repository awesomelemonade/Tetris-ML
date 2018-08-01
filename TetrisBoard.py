import numpy as np
from TetrisConstants import *
import pygame
from Color import Color

class TetrisBoard:
	def __init__(self, width, height, renderWidth, renderHeight, seed):
		self.random = np.random.RandomState(seed) # Initialize random with seed
		self.width = width
		self.height = height
		self.grid = self.createBlankGrid()
		self.startX = int(width / 2 - TetrisConstants.TEMPLATE_WIDTH / 2)
		self.startY = 0
		self.fallingPiece = self.getRandomNewPiece()
		self.nextPiece = self.getRandomNewPiece()
		self.score = 0
		self.level = 1
	def createBlankGrid(self):
		grid = np.chararray((self.width, self.height))
		grid[:] = BLANK
		return grid
	def isCompleteLine(self, grid, y):
		return np.all(grid[:, y].decode() != BLANK)
	def removeCompletedLines(self):
		numLinesRemoved = 0
		for y in range(0, self.height): # Go from bottom up
			if self.isCompleteLine(self.grid, y):
				self.grid[:, 1 : y + 1] = self.grid[:, :y]
				self.grid[:, 0] = BLANK
				numLinesRemoved += 1
		#scoring
		self.changeScore(numLinesRemoved)

	def isOnBoard(self, x, y):
		return x >= 0 and x < self.width and y >= 0 and y < self.height
	def isValidPosition(self, piece, adjustX=0, adjustY=0, rotation=None):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if self.getTemplate(piece, x, y, rotation) == BLANK:
					continue
				if not self.isOnBoard(piece.x + x + adjustX, piece.y + y + adjustY):
					return False
				if self.grid[piece.x + x + adjustX, piece.y + y + adjustY].decode() != BLANK:
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
	def rotateFallingPiece(self, rotate):
		targetRotation = (self.fallingPiece.rotation + rotate) % len(TetrisConstants.PIECES[self.fallingPiece.type].template)
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
			self.fallingPiece = self.nextPiece
			#check if anything is on top
			if(not self.isValidPosition(self.fallingPiece)):
				return False #loss condition
			self.nextPiece = self.getRandomNewPiece()
		else:
			self.fallingPiece.y += 1
		return True #normal condition
	def render(self, screen, renderWidth, renderHeight, shiftx = 0, shifty = 0):
		gridWidth = renderWidth / (3 * self.width)
		gridHeight = renderHeight / (self.height)
		# Render Grid
		for x in range(self.width):
			for y in range(self.height):
				if not self.grid[x, y].decode() == BLANK:
					pygame.draw.rect(screen, self.border(TetrisConstants.PIECES[self.grid[x, y].decode()].color), [x * gridWidth + shiftx, y * gridHeight + shifty, gridWidth, gridHeight], 3)
					pygame.draw.rect(screen, TetrisConstants.PIECES[self.grid[x, y].decode()].color , [x * gridWidth + shiftx, y * gridHeight + shifty, gridWidth, gridHeight])
				else:
					pygame.draw.rect(screen, Color.BLACK, [x * gridWidth +shiftx, y * gridHeight + shifty, gridWidth, gridHeight])
		# Render Falling Piece
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not self.getTemplate(self.fallingPiece, x, y) == BLANK:
					pygame.draw.rect(screen, self.border(TetrisConstants.PIECES[self.fallingPiece.type].color), [(self.fallingPiece.x + x) * gridWidth + shiftx, (self.fallingPiece.y + y) * gridHeight + shifty, gridWidth, gridHeight], 3)
					pygame.draw.rect(screen, TetrisConstants.PIECES[self.fallingPiece.type].color, [(self.fallingPiece.x + x) * gridWidth + shiftx, (self.fallingPiece.y + y) * gridHeight + shifty, gridWidth, gridHeight])
		# Render Next Piece
		pygame.draw.rect(screen, (0, 130, 255), [100, 100, gridWidth * 5, gridHeight * 5])
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not self.getTemplate(self.nextPiece, x, y) == BLANK:
					pygame.draw.rect(screen, self.border(TetrisConstants.PIECES[self.nextPiece.type].color), [(self.nextPiece.x + x) * gridWidth + 10, (self.nextPiece.y + y) * gridHeight + 100, gridWidth, gridHeight], 3)
					pygame.draw.rect(screen, TetrisConstants.PIECES[self.nextPiece.type].color, [(self.nextPiece.x + x) * gridWidth + 10, (self.nextPiece.y + y) * gridHeight + 100, gridWidth, gridHeight])
	def changeScore(self, lines):
		if(lines == 1):
			score = 40
		elif(lines == 2):
			score = 100
		elif(lines== 3):
			score = 300
		else:
			score = 1200
		self.score += self.level * score
	#onyl for styling
	def border(self, color):
		arr = np.array(color, dtype = np.int)
		center = ((arr < 128) - .5) * 2
		return tuple(arr + center * 30)
