import numpy as np


class GameOfLife(object):
	def __init__(self, world):
		self.world = world
		self.next_world = np.array(world, copy=True)

	def next_generation(self):
		"""Rules for the game:
		    Any live cell with fewer than two live neighbors dies, as if by underpopulation.
		    Any live cell with two or three live neighbors lives on to the next generation.
		    Any live cell with more than three live neighbors dies, as if by overpopulation.
		    Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.
		"""
		for (x, y), element in np.ndenumerate(self.world):
			alive_neighbours = sum(self._get_neighbours(x, y))
			if element:
				if alive_neighbours < 2 or alive_neighbours > 3:
					self.next_world[x, y] = False
			else:
				if alive_neighbours == 3:
					self.next_world[x, y] = True
		self.world = np.array(self.next_world, copy=True)

	def _get_neighbours(self, x, y):
		res = np.array([], dtype=np.bool)
		for i in range(-1, 2):
			for j in range(-1, 2):
				if i or j:
					res = np.append(res, self.world[(x + i) % self.world.shape[0], (y + j) % self.world.shape[1]])
		return res
