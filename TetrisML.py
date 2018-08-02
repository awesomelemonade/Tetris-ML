import numpy as np
import mygrad as mg
from mygrad.nnet.activations import softmax
from mygrad.nnet.losses import softmax_crossentropy
from TetrisConstants import *
import time

class TetrisModel:
	def __init__(self):
		self.H = 200 # Number of hidden neurons
		self.batch_size = 10 # Play multiple games simultaneously
		self.learning_rate = 1e-4
		self.model = {}
		self.model['W1'] = mg.Tensor(np.random.randn(200, self.H))
		self.model['W2'] = mg.Tensor(np.random.randn(self.H, 5))
	def policyForward(self, data):
		data = mg.Tensor(data.astype(int)) # Convert to Tensor
		hiddenNeurons = mg.matmul(data, self.model['W1']) # Matrix multiply weights #1
		hiddenNeurons[hiddenNeurons < 0] = 0 # ReLU
		outNeurons = mg.matmul(hiddenNeurons, self.model['W2']) # Matrix multiply weights #2
		return outNeurons
	def getDerivatives(self): # Extracts derivatives from backprop
		return (self.model['W1'].grad, self.model['W2'].grad)
	def gradientDescent(self, derivatives, rewards): # rewards are delta score
		rewards = np.array(rewards, dtype=np.float64)
		# derivatives = list of list
		dW1, dW2 = zip(*derivatives)
		dW1 = np.moveaxis(np.array(dW1), 0, -1)
		dW2 = np.moveaxis(np.array(dW2), 0, -1)
		rewards[-1] = - 1 / len(rewards) # discourage all steps slightly because we lost
		rewards = np.cumsum(rewards[::-1])[::-1]
		self.model['W1'] += np.sum(self.learning_rate * dW1 * rewards, axis=-1)
		self.model['W2'] += np.sum(self.learning_rate * dW2 * rewards, axis=-1)
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
	def step(self, tetrisBoard): # Called each step of the game
		temp = time.time()
		data = self.preprocess(tetrisBoard)
		print("Preprocess: {}".format(time.time() - temp))
		temp = time.time()
		outNeurons = self.model.policyForward(data)
		print("Forward: {}".format(time.time() - temp))
		temp = time.time()
		probabilities = softmax(outNeurons)
		choice = np.random.choice(np.arange(len(probabilities)), p=probabilities)
		reward = np.zeros(probabilities.shape, dtype=int)
		reward[choice] = 1
		print("Choice: {}".format(time.time() - temp))
		temp = time.time()
		loss = softmax_crossentropy(outNeurons.reshape(1, len(outNeurons)), reward)
		loss.backward()
		print("Backprop: {}".format(time.time() - temp))
		temp = time.time()
		# Store the derivatives - model['W1'] and model['W2']
		self.derivatives.append(self.model.getDerivatives())
		loss.null_gradients()
		# Calculate delta score, store
		deltaScore = tetrisBoard.score - self.prevscores.get(tetrisBoard, 0)
		self.prevscores[tetrisBoard] = tetrisBoard.score
		self.rewards.append(deltaScore)
		print("Record: {}".format(time.time() - temp))
		return choice
	def gameover(self): # Called when lose to gradient descent
		self.model.gradientDescent(self.derivatives, self.rewards)
		self.derivatives = []
		self.rewards = []
