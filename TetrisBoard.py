import numpy as np
from TetrisConstants import *
import pygame

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
	def createBlankGrid(self):
		grid = np.chararray((self.width, self.height))
		grid[:] = BLANK
		return grid
	def isCompleteLine(self, grid, y):
		return np.all(grid[:, y].decode() != BLANK)
	def removeCompletedLines(self):
		numLinesRemoved = 0
		for y in range(self.height - 1, -1, -1): # Go from bottom up
			if self.isCompleteLine(self.grid, y):
				numLinesRemoved += 1
		# Move Everything Down
		self.grid[:, numLinesRemoved:] = self.grid[:, :self.height - numLinesRemoved]
		self.grid[:, :numLinesRemoved] = BLANK
	def isOnBoard(self, x, y):
		return x >= 0 and x < self.width and y >= 0 and y < self.height
	def isValidPosition(self, piece, adjustX=0, adjustY=0):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if self.getTemplate(piece, x, y) == BLANK:
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
	def getTemplate(self, piece, x=None, y=None):
		if x is None or y is None:
			return TetrisConstants.PIECES[piece.type].template[piece.rotation]
		else:
			return TetrisConstants.PIECES[piece.type].template[piece.rotation][x][y]
	def getRandomNewPiece(self):
		pieceType = self.getRandomPieceType()
		return Piece(self.startX, self.startY, pieceType, self.getRandomRotation(pieceType))
	def getRandomPieceType(self):
		return self.random.choice(list(TetrisConstants.PIECES.keys()))
	def getRandomRotation(self, pieceType):
		return self.random.randint(0, len(TetrisConstants.PIECES[pieceType].template))
	def update(self):
		if not self.isValidPosition(self.fallingPiece, adjustY=1):
			# falling piece has landed, set it on the board
			self.setPiece(self.fallingPiece)
			self.fallingPiece = self.nextPiece
			self.nextPiece = self.getRandomNewPiece()
			self.removeCompletedLines()
		else:
			self.fallingPiece.y += 1
	def render(self, screen, renderWidth, renderHeight):
		gridWidth = renderWidth / self.width
		gridHeight = renderHeight / self.height
		# Render Grid
		for x in range(self.width):
			for y in range(self.height):
				if not self.grid[x, y].decode() == BLANK:
					pygame.draw.rect(screen, TetrisConstants.PIECES[self.grid[x, y].decode()].color, [x * gridWidth, y * gridHeight, gridWidth, gridHeight])
		# Render Falling Piece
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not self.getTemplate(self.fallingPiece, x, y) == BLANK:
					pygame.draw.rect(screen, TetrisConstants.PIECES[self.fallingPiece.type].color, [(self.fallingPiece.x + x) * gridWidth, (self.fallingPiece.y + y) * gridHeight, gridWidth, gridHeight])
		# Render Next Piece - TODO
