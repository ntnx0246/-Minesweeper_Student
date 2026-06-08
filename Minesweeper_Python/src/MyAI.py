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
		
		# For debug
		self.__guess_count = 0
		self.__safe_count = 0
		self.__flag_count = 0

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

			constraints = []
			for (x, y), num in self.__board.items():
				neighbors = self.getNeighbors(x, y)
				covered = frozenset(n for n in neighbors if n in self.__covered)
				flagged = sum(1 for n in neighbors if n in self.__mines)
				if len(covered) != 0:
					constraints.append((covered, num - flagged))

			new_mines = 0
			new_set = frozenset()
			for A in constraints:
				for B in constraints:
					# A must be a subset of B in this case for us to use this
					if A[0] < B[0]:
						new_set   = B[0] - A[0]
						new_mines = B[1] - A[1]
						# Apply the two cases below

						if new_mines == 0:
							# All tiles in new_set are safe
							for tile in new_set:
								if tile not in self.__safe_moves and tile not in self.__mines:
									self.__safe_moves.append(tile)
									isDifferent = True

						if new_mines == len(new_set):
							# All tiles in new_set are mines
							for tile in new_set:
								if tile not in self.__mines:
									self.__mines.add(tile)
									self.__flag_moves.append(Action(AI.Action.FLAG, tile[0], tile[1]))
									isDifferent = True
         
            
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
       
			# Calculate remaining mines
			mines_remaining = self.__totalMines - len(self.__mines)
			# The amount that remains covered
			covered_count = len(self.__covered)
			
			# If we uncovered all the mines, we can uncover all other tiles
			if mines_remaining == 0 and covered_count > 0:
				# All remaining covered tiles are safe
				for tile in self.__covered:
					if tile not in self.__safe_moves and tile not in self.__mines:
						self.__safe_moves.append(tile)
						isDifferent = True
			
			# If only mines remain, we can flag every other tile
			if mines_remaining == covered_count and covered_count > 0:
				# All remaining covered tiles are mines
				for tile in list(self.__covered):
					if tile not in self.__mines:
						self.__mines.add(tile)
						self.__flag_moves.append(Action(AI.Action.FLAG, tile[0], tile[1]))
						isDifferent = True
                
		
		# Propagation stalled: try backtracking to find guaranteed safe/mine tiles
		frontier_probs = {}
		interior_prob = None
		if len(self.__safe_moves) == 0 and len(self.__flag_moves) == 0 and len(self.__covered) > 0:
			safe, mines, frontier_probs, interior_prob = self.backtrackDeductions()
			for tile in safe:
				if tile not in self.__mines:
					self.__safe_moves.append(tile)
			for tile in mines:
				if tile not in self.__mines:
					self.__mines.add(tile)
					self.__flag_moves.append(Action(AI.Action.FLAG, tile[0], tile[1]))

		# Choose a flag move if there is one
		if len(self.__flag_moves) > 0:
			move = self.__flag_moves.popleft()
			self.__flag_count += 1
			self.__lastAction = AI.Action.FLAG
			self.__lastX, self.__lastY = move.getX(), move.getY()
			self.__covered.discard((self.__lastX, self.__lastY))
			return move
		
		# Choose a safe move if there is one
		if len(self.__safe_moves) > 0:
			self.__safe_count += 1
			move = self.__safe_moves.popleft()
			self.__covered.discard(move)
			self.__lastX, self.__lastY = move
			self.__lastAction = AI.Action.UNCOVER

			return Action(AI.Action.UNCOVER, move[0], move[1])

		# No guaranteed move: pick the covered tile least likely to be a mine
		if(len(self.__covered) > 0):
			self.__guess_count += 1
			move = self.chooseGuess(frontier_probs, interior_prob)
			self.__covered.discard(move)
			self.__lastX, self.__lastY = move
			self.__lastAction = AI.Action.UNCOVER
			return Action(AI.Action.UNCOVER, move[0], move[1])

		# Probability based guessing
		print(f"Game end. Guesses: {self.__guess_count}, Safe: {self.__safe_count}, Flags: {self.__flag_count}")
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

	def chooseGuess(self, frontier_probs, interior_prob):
		#Pick the covered tile least likely to be a mine

		candidates = []  # (probability, tile)
		for tile, p in frontier_probs.items():
			if tile in self.__covered:
				candidates.append((p, tile))

		# Interior tiles (no uncovered neighbor) all share one probability
		interior = [t for t in self.__covered
		            if t not in frontier_probs and not self.hasUncoveredNeighbor(t[0], t[1])]
		if interior:
			if interior_prob is None:
				mines_remaining = self.__totalMines - len(self.__mines)
				expected_frontier = sum(frontier_probs.values())
				interior_prob = (mines_remaining - expected_frontier) / len(interior)
			interior_prob = min(1.0, max(0.0, interior_prob))
			for t in interior:
				candidates.append((interior_prob, t))

		#If no tile has a probability (e.g. component too large to enumerate)
		if not candidates:
			return next(iter(self.__covered))

		# Choose best candidate based on lowest probability of being a mine
		best_prob = min(p for p, _ in candidates)
		ties = [t for p, t in candidates if p <= best_prob + 1e-9]
		
		# Breaks ties by preffering guesses that reveal more 
		ties.sort(key=lambda t: (-len(self.getNeighbors(t[0], t[1])), t))
		return ties[0]

	def backtrackDeductions(self):
		# Builds constraints
		constraints = []

		# Flips board representation with constraints being the main object
		var_set = set()
		for (x, y), num in self.__board.items():
			covered = [n for n in self.getNeighbors(x, y) if n in self.__covered]
			if not covered:
				continue
			flagged = sum(1 for n in self.getNeighbors(x, y) if n in self.__mines)
			constraints.append((covered, num - flagged))
			var_set.update(covered)

		if not var_set:
			return set(), set(), {}, None

		# Map each variable to the indices of constraints that involve it
		var_constraints = {v: [] for v in var_set}
		for ci, (vars_, _) in enumerate(constraints):
			for v in vars_:
				var_constraints[v].append(ci)

		# Find the connected components (they share a constraint)
		# Use a DFS in order to find adjacent variables that share constraints
		visited = set()
		safe, mines = set(), set()
		solved = []        # (comp, dist, var_dist) for each enumerated component
		all_solved = True
		for start in var_set:
			if start in visited:
				continue
			comp = []
			stack = [start]
			visited.add(start)
			while stack:
				cur = stack.pop()
				comp.append(cur)
				for ci in var_constraints[cur]:
					for nb in constraints[ci][0]:
						if nb not in visited:
							visited.add(nb)
							stack.append(nb)

			# Finds the probability of each variable being a mine by forcing combinations of mines
			result = self.solveComponent(comp, constraints, var_constraints)
			
			# If component is too large just skip this step
			if result is None:
				all_solved = False
				continue

			# Store results of backtracking for the component into dist, var_dist
			dist, var_dist = result

			# Sum of all valid assignments for the component
			total = sum(dist.values())
			if total == 0:
				continue

			# Local deductions are valid regardless of the global mine budget
			for v in comp:
				mc = sum(var_dist[v].values())
				if mc == 0:
					safe.add(v)
				elif mc == total:
					mines.add(v)
			solved.append((comp, dist, var_dist))

		interior_count = len(self.__covered) - len(var_set)
		mines_remaining = self.__totalMines - len(self.__mines)

		# With every component enumerated we can weight layouts by the global mine 
		if all_solved and solved:
			probs, interior_prob, gsafe, gmines = self.globalMarginals(
				solved, interior_count, mines_remaining)
			safe |= gsafe
			mines |= gmines
			return safe, mines, probs, interior_prob

		# Fallback: per-component local marginals (some component was too large)
		probs = {}
		for comp, dist, var_dist in solved:
			total = sum(dist.values())
			for v in comp:
				probs[v] = sum(var_dist[v].values()) / total
		return safe, mines, probs, None

	def globalMarginals(self, solved, interior_count, mines_remaining):
		#Exact frontier marginals using the global mine budget. Each frontier
		#layout with M mines is weighted by C(interior_count, mines_remaining - M),
		#the number of ways to place the leftover mines among interior tiles.
		import math

		def weight(M):
			j = mines_remaining - M
			if j < 0 or j > interior_count:
				return 0
			return math.comb(interior_count, j)

		# Global distribution of total frontier mines (convolution of components)
		def convolve(dists):
			acc = {0: 1}
			for d in dists:
				nxt = {}
				for m, c in acc.items():
					for k, ck in d.items():
						nxt[m + k] = nxt.get(m + k, 0) + c * ck
				acc = nxt
			return acc

		comp_dists = [d for _, d, _ in solved]
		G = convolve(comp_dists)
		Z = sum(c * weight(M) for M, c in G.items())
		if Z == 0:
			return {}, None, set(), set()

		probs, gsafe, gmines = {}, set(), set()
		for idx, (comp, dist, var_dist) in enumerate(solved):
			rest = convolve(comp_dists[:idx] + comp_dists[idx + 1:])
			for v in comp:
				num = 0
				for k, ckv in var_dist[v].items():
					for m, cm in rest.items():
						w = weight(k + m)
						if w:
							num += ckv * cm * w
				probs[v] = num / Z
				if num == 0:
					gsafe.add(v)
				elif num == Z:
					gmines.add(v)

		interior_prob = None
		if interior_count > 0:
			num = sum(c * weight(M) * (mines_remaining - M) for M, c in G.items()
			          if weight(M))
			interior_prob = num / (Z * interior_count)
		return probs, interior_prob, gsafe, gmines

	def solveComponent(self, comp, constraints, var_constraints):
		#Count, per variable in comp, how many valid assignments make it a mine.
		
		if len(comp) > 40:
			return None

		# Order variables so each shares a constraint with earlier ones (tightens pruning)
		comp = self.orderComponent(comp, constraints, var_constraints)

		rel = set()
		for v in comp:
			rel.update(var_constraints[v])
		csum = {ci: 0 for ci in rel}
		cunassigned = {ci: len(constraints[ci][0]) for ci in rel}

		# dist[k] = number of solutions using exactly k mines in this component.
		# var_dist[v][k] = number of those k-mine solutions where v is a mine.
		dist = {}
		var_dist = {v: {} for v in comp}
		assignment = {}
		mines_used = [0]
		budget = [500000]

		# Recurses thorugh all mine assignments to variables in comp, pruning if necessary
		def recurse(i):
			if budget[0] <= 0:
				return False
			budget[0] -= 1
			if i == len(comp):
				k = mines_used[0]
				dist[k] = dist.get(k, 0) + 1
				for v in comp:
					if assignment[v]:
						vd = var_dist[v]
						vd[k] = vd.get(k, 0) + 1
				return True
			v = comp[i]
			for val in (0, 1):
				assignment[v] = val
				mines_used[0] += val
				ok = True
				for ci in var_constraints[v]:
					csum[ci] += val
					cunassigned[ci] -= 1
					req = constraints[ci][1]
					if csum[ci] > req or csum[ci] + cunassigned[ci] < req:
						ok = False
				if ok and not recurse(i + 1):
					# Budget exhausted: undo and abort
					for ci in var_constraints[v]:
						csum[ci] -= val
						cunassigned[ci] += 1
					mines_used[0] -= val
					return False
				for ci in var_constraints[v]:
					csum[ci] -= val
					cunassigned[ci] += 1
				mines_used[0] -= val
			return True

		if not recurse(0):
			return None
		return dist, var_dist

	def orderComponent(self, comp, constraints, var_constraints):
		# Order vars by BFS over the constraint graph so neighbors stay adjacent
		comp_set = set(comp)
		ordered = []
		seen = set()
		for seed in comp:
			if seed in seen:
				continue
			queue = deque([seed])
			seen.add(seed)
			while queue:
				cur = queue.popleft()
				ordered.append(cur)
				for ci in var_constraints[cur]:
					for nb in constraints[ci][0]:
						if nb in comp_set and nb not in seen:
							seen.add(nb)
							queue.append(nb)
		return ordered

		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
