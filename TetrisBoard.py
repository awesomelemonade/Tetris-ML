import numpy as np

class TetrisBoard:
	BLANK = '.'
	def __init__(self, width, height, renderWidth, renderHeight, seed):
		self.random = # TODO: Initialize Random with Seed
		self.width = width
		self.height = height
		self.grid = createBlankGrid()
		self.startX = int(width / 2 - TetrisConstants.TEMPLATE_WIDTH / 2)
		self.startY = 0
		self.fallingPiece = Piece(startX, startY, getRandomPieceType(), )
	def createBlankGrid(self):
		grid = np.chararray((self.width, self.height))
		grid[:] = BLANK
		return grid
	def isCompleteLine(self, grid, y):
		return np.all(board[:, y] != BLANK)
	def removeCompletedLines(self):
		numLinesRemoved = 0
		for y in range(self.height, 0, -1) - 1:
			if isCompleteLine(self.grid, y):
				numLinesRemoved += 1
		self.grid[:, numLinesRemoved:] = self.grid[:, :height - numLinesremoved]
		self.grid[:, :numLinesRemoved] = BLANK
	def isOnBoard(x, y):
		return x >= 0 and x < self.width and y >= 0 and y < self.height
	def isValidPosition(piece, adjustX=0, adjustY=0):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if getTemplate(piece) == BLANK
					continue
				if not isOnBoard(piece.x + x + adjustX, piece.y + y + adjustY):
					return False
				if self.grid[piece.x + x + adjustX, piece.y + y + adjustY] != BLANK:
					return False
		return True
	def setPiece(self, piece):
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not TetrisConstants.PIECES[piece.type] == BLANK:
					grid[piece.x + x, piece.y + y] = getTemplate(piece)[x, y]
	def getTemplate(self, piece):
		return TetrisConstants.PIECES[piece.type].template[piece.rotation]
	def getRandomNewPiece(self):
		pieceType = getRandomPieceType()
		return Piece(self.startX, self.startY, pieceType, getRandomRotation(pieceType))
	def getRandomPieceType(self):
		return random.randint(len(PIECES.keys()))
	def getRandomRotation(self, pieceType):
		return random.randint(len(PIECES[pieceType].template))
	def update(self):
		
	def render(self, screen, renderWidth, renderHeight):
		for x in range(self.width):
			for y in range(self.height):
				pygame.draw.rect(screen, TetrisConstants.PIECES[self.grid[x, y]].color, [x, y, renderWidth/width, renderHeight/height])
