import numpy as np
import mygrad as mg
from mygrad.nnet.activations import softmax
from mygrad.nnet.losses import softmax_crossentropy
from TetrisConstants import *

class TetrisModel:
	def __init__(self):
		self.H = 200 # Number of hidden neurons
		self.batch_size = 10 # Play multiple games simultaneously
		self.learning_rate = 1e-4
		self.model = {}
		self.model['W1'] = mg.Tensor(np.random.randn(200, self.H))
		self.model['W2'] = mg.Tensor(np.random.randn(self.H, 10))
	def policyForward(self, data):
		data = mg.Tensor(data.astype(int)) # Convert to Tensor
		hiddenNeurons = mg.matmul(data, self.model['W1']) # Matrix multiply weights #1
		hiddenNeurons[hiddenNeurons < 0] = 0 # ReLU
		outNeurons = mg.matmul(hiddenNeurons, self.model['W2']) # Matrix multiply weights #2
		return outNeurons
	def getDerivatives(self): # Extracts derivatives from backprop
		return (self.model['W1'].grad, self.model['W2'].grad)
	def gradientDescent(self, derivatives, rewards): # rewards are delta score
		# rewards = list of list of numbers
		rewards = np.array(rewards) # 2d array
		# derivatives = list of list of tuples
		derivatives = np.moveaxis(np.array(derivatives), -1, 0)
		rewards = np.cumsum(rewards[:, ::-1], axis=1)[:, ::-1]
		print(rewards.shape)
		rewards -= 1
		model['W1'] += learning_rate * derivatives[0, :, :] * rewards
		model['W2'] += learning_rate * derivatives[1, :, :] * rewards
class TetrisML:
	def __init__(self):
		self.model = TetrisModel()
		self.derivatives = []
		self.rewards = []
		self.prevscores = {}
	def preprocess(self, tetrisBoard): # Preprocesses the tetris board to a flattened numpy array
		grid = tetrisBoard.grid != BLANK
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not tetrisBoard.getTemplate(tetrisBoard.fallingPiece, x, y) == BLANK:
					grid[tetrisBoard.fallingPiece.x + x, tetrisBoard.fallingPiece.y + y] = 2
		return grid.ravel()
	def step(self, tetrisBoards):
		self.derivatives.append([])
		self.rewards.append([])
		for tetrisBoard in tetrisBoards:
			self.handle(tetrisBoard)
	def handle(self, tetrisBoard): # Called each step of the game
		data = self.preprocess(tetrisBoard)
		outNeurons = self.model.policyForward(data)
		probabilities = softmax(outNeurons)
		choice = np.random.choice(np.arange(len(probabilities)), p=probabilities)
		reward = np.zeros(probabilities.shape, dtype=int)
		reward[choice] = 1
		loss = softmax_crossentropy(outNeurons.reshape(1, 10), reward)
		loss.backward()
		# Store the derivatives - model['W1'] and model['W2']
		self.derivatives[-1].append(self.model.getDerivatives())
		loss.null_gradients()
		# Calculate delta score, store
		deltaScore = tetrisBoard.score - self.prevscores.get(tetrisBoard, 0)
		self.prevscores[tetrisBoard] = tetrisBoard.score
		self.rewards[-1].append(deltaScore)
		return choice
	def gameover(self): # Called when lose to gradient descent
		gradientDescent(self.derivatives, self.rewards)
		self.derivatives = []
		self.rewards = []
