def pretty_print(arr):
	"""
	pretty prints the 2d game state of a game of life
	:param arr: a numpy 2d-array
	"""
	print('\n'.join((''.join(('▓' if j else '░' for j in arr[i]))) for i in range(arr.shape[0])))
