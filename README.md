# Tetris-ML
Cog*works Final Project; Team: Echo Dot Product; Python 3.6

# What is Tetris-ML
Tetris-ML is an attempt to have machine learning play tetris using reinforcement learning. This project's algorithm was inspired by Karpathy's [Pong from Pixels](http://karpathy.github.io/2016/05/31/rl/), but many modifications were necessary in order to convert it from a simple game like pong into tetris.

# Notable Files
  - ```installdependencies.sh``` - Script to download dependencies (excluding python, mygrad, mynn)
    - MyGrad: https://github.com/rsokl/MyGrad; MyNN is not a public repository (8/4/18)
  - ```TetrisML.py``` - The ancestor of all the AIs - The Ancient One
  - ```ConvModel.py``` - First attempt at implementing CNNs
  - ```game.py``` - Run this file if you want to play tetris yourself on this engine!
  - ```NewAlgo.py``` - Height based reward system
  - ```Color.py``` - Colors!!!
  - ```TetrisBoard.py``` - Core engine handling the board
  - ```TetrisConstants.py``` - Constants such as templates of pieces - you can mess with it to have custom pieces
  - ```NewTrainerUnbatched.py``` - Recommended training - using game time as reward
  - Checkpoints (when you run NewTrainerUnbatched.py) will appear in the checkpoints folder
