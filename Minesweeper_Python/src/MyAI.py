# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
from collections import deque

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.__startX = startX
		self.__startY = startY

		self.__board = {} # (x, y) -> number
		self.__covered = set() # Coordinates of unkonwn tiles
		self.__safe_moves = deque() # Coordinates of safe moves
		self.__mines = set() # Coordinates of known mines
		self.__flag_moves = deque() # Queue of moves to flag mines
		

		#Initialize covered set with all coordinates
		for x in range(colDimension):
			for y in range(rowDimension):
				self.__covered.add((x, y))

		self.__lastX = startX
		self.__lastY = startY
		self.__lastAction = AI.Action.UNCOVER # First tile is safe and uncovered for us

		self.__covered.discard((startX, startY))
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		# Update the board with the revealed numbers by the last action
		if(self.__lastAction == AI.Action.UNCOVER and number >= 0):
			self.__board[(self.__lastX, self.__lastY)] = number

		isDifferent = True
		while isDifferent:
			isDifferent = False

			# Checks for every number tiled on the board
			for (x, y), num in self.__board.items():

				# Get the neighbors of the tile in a list of (x, y) coordinates
				neighbors = self.getNeighbors(x, y)
				
				# Finds covered neighbors by checking if neighbor is in the covered set and flagged neighbors by checking if neighbor is in the mines set
				covered_neighbors = [n for n in neighbors if n in self.__covered]
				flagged_neighbors = [n for n in neighbors if n in self.__mines]

				# All the covered mines have to be safe
				if num == len(flagged_neighbors) and len(covered_neighbors) > 0:
					for n in covered_neighbors:
						if n not in self.__safe_moves and n not in self.__mines:
							self.__safe_moves.append(n)
							isDifferent = True
			
				# Rest of flags must be mines
				if num == len(flagged_neighbors) + len(covered_neighbors) and len(covered_neighbors) > 0:
					for n in covered_neighbors:
						if n not in self.__mines:
							self.__mines.add(n)
							self.__flag_moves.append(Action(AI.Action.FLAG, n[0], n[1]))
							isDifferent = True
		
		# Choose a flag move if there is one
		if len(self.__flag_moves) > 0:
			move = self.__flag_moves.popleft()
			self.__lastAction = AI.Action.FLAG
			self.__lastX, self.__lastY = move.getX(), move.getY()
			self.__covered.discard((self.__lastX, self.__lastY))
			return move
		
		# Choose a safe move if there is one
		if len(self.__safe_moves) > 0:
			move = self.__safe_moves.popleft()
			self.__covered.discard(move)
			self.__lastX, self.__lastY = move
			self.__lastAction = AI.Action.UNCOVER

			return Action(AI.Action.UNCOVER, move[0], move[1])

		# Choose a random tile if there is no guarenteed safe move or flagged move
		# Choose a random tile that has nothing uncovered bordering it if possible
		if(len(self.__covered) > 0):
			# uncovered = set()
			# for tile in self.__covered:
			# 	has_neighboor = self.hasUncoveredNeighbor(tile[0], tile[1])
			# 	if has_neighboor == False:
			# 		uncovered.add(tile)
     
			# if len(uncovered) != 0:
			# 	move = uncovered.pop()
			# 	self.__lastX, self.__lastY = move
			# 	self.__lastAction = AI.Action.UNCOVER
			# 	return Action(AI.Action.UNCOVER, move[0], move[1])

			move = self.__covered.pop()
			self.__lastX, self.__lastY = move
			self.__lastAction = AI.Action.UNCOVER
			return Action(AI.Action.UNCOVER, move[0], move[1])
		
		# Board is uncovered so leave game
		return Action(AI.Action.LEAVE)
		

	def getNeighbors(self, x, y):
		neighbors = []
		for i in range(-1, 2):
			for j in range(-1, 2):
				if (0 <= x + i < self.__colDimension) and (0 <= y + j < self.__rowDimension) and not (i == 0 and j == 0):
					neighbors.append((x + i, y + j))
		return neighbors

	def hasUncoveredNeighbor(self, x, y):
		for i in range(-1, 2):
			for j in range(-1, 2):
				if (0 <= x + i < self.__colDimension) and (0 <= y + j < self.__rowDimension) and not (i == 0 and j == 0) and ((x + i, y + j) in self.__board):
					return True
		return False

		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

#Todo:
# Optimize to use effective number instead of recalculating everytime. 
# Implement constraint logic
# Implement probability checking when guessing
# Implement backtracking	