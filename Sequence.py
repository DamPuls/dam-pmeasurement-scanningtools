# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Sequence
# Purpose:
#
# Author:      ED
#
# Created:     04/03/2017
# Copyright:   (c) ED 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from __future__ import print_function
from Grid import Grid
import numpy as np

class SequenceError (Exception):
	"""Sequence error"""
# end class SequenceError

class Sequence(object):
	def __init__(self, grid):
		self.grid = grid
		self.dimensions = (grid.NX, grid.NY, grid.NZ)
		self.gridSize = grid.gridSize
		self.gridIndex = np.zeros((self.gridSize,3), dtype=int)

	def getPosition(self, N):
		gridIndex = self.getGridIndex(N)
		position = self.grid.getPosition(gridIndex[0], gridIndex[1], gridIndex[2])
		return position
	# end def getPosition

	def getDimensions(self):
		return self.dimensions
	# end def getDimensions

	def getGridIndex(self, N):
		if (N < 0) or (N > (self.gridSize-1)):
			raise SequenceError("Index={} out of bounds [0, {}]".format(N, self.gridSize-1))
		# end if
		return self.gridIndex[N]
	# end def getGridIndex
# end class Sequence


class SequenceRectDirect  (Sequence):
	def __init__(self, grid):
		Sequence.__init__(self, grid)
		positiveSenseX = True
		positiveSenseY = True
		indexCount = 0

		for indexZ in range(grid.NZ):
			if positiveSenseY:
				indexYY = range(grid.NY)
				positiveSenseY = False
			else:
				indexYY = range(grid.NY-1,-1,-1)
				positiveSenseY = True
			# end if

			for indexY in indexYY:
				if positiveSenseX:
					indexXX = range(grid.NX)
					positiveSenseX = False
				else:
					indexXX = range(grid.NX-1,-1,-1)
					positiveSenseX = True
				# end if

				for indexX in indexXX:
					#(posX, posY, posZ) = grid.getPosition(indexX, indexY, indexZ)
					self.gridIndex[indexCount] = [indexX, indexY, indexZ]
					#self.seq.append([posX, posY, posZ])
					indexCount += 1
				# end for
			# end for
		# end for
	# end def __init__
# end class SequenceRectDirect


class SequenceRectCenter  (Sequence):
	def __init__(self, grid):
		Sequence.__init__(self, grid)

		POSC = [[[True]*grid.NX]*grid.NY]*grid.NZ

		indexCount = 0
		self.gridIndex[indexCount] = [grid.NX/2, grid.NY/2, 0]
		indexCount += 1

		for indexZ in range(grid.NZ):
			indexX = grid.NX/2
			indexY = grid.NY/2
			delta  =  1
			direc  = -1
			outOfPlan = False

			while True:
				for indexYY in range(delta):
					indexY += direc
					if (indexY == -1) or (indexY == grid.NY):
						outOfPlan = True
						break
					else:
						POSC[indexZ][indexY][indexX] = False
						self.gridIndex[indexCount] = [indexX, indexY, indexZ]
						indexCount += 1
					# end if
				# end for
				if outOfPlan:
					break
				# end if

				for indexXX in range(delta):
					indexX += direc
					if (indexX == -1) or (indexX == grid.NX):
						outOfPlan = True
						break
					else:
						POSC[indexZ][indexY][indexX] = False
						self.gridIndex[indexCount] = [indexX, indexY, indexZ]
						indexCount += 1
					# end if
				# end for
				if outOfPlan:
					break
				# end if

				direc = -direc
				delta += 1
			# end while
		# end for

		if grid.NX>grid.NY:
			#x->z
			#y->y
			#z->x
			positiveSenseZ = True
			positiveSenseY = True

			for indexX in range(grid.NX):
				if positiveSenseY:
					indexYY = range(grid.NY)
					positiveSenseY = False
				else:
					indexYY = range(grid.NY-1,-1,-1)
					positiveSenseY = True
				# end if

				for indexY in indexYY:
					if positiveSenseZ:
						indexZZ = range(grid.NZ)
						positiveSenseZ = False
					else:
						indexZZ = range(grid.NZ-1,-1,-1)
						positiveSenseZ = True
					# end if

					for indexZ in indexZZ:
						if POSC[indexZ][indexY][indexX]:
							self.gridIndex[indexCount] = [indexX, indexY, indexZ]
							indexCount += 1
						# end if
					# end for
				# end for
			# end for
		# end if

		if grid.NY>grid.NX:
			#x->x
			#y->z
			#z->y
			positiveSenseX = True
			positiveSenseZ = True
			#indexCount = 0

			for indexY in range(grid.NY):
				if positiveSenseZ:
					indexZZ = range(grid.NZ)
					positiveSenseZ = False
				else:
					indexZZ = range(grid.NZ-1,-1,-1)
					positiveSenseZ = True
				# end if

				for indexZ in indexZZ:
					if positiveSenseX:
						indexXX = range(grid.NX)
						positiveSenseX = False
					else:
						indexXX = range(grid.NX-1,-1,-1)
						positiveSenseX = True
					# end if

					for indexX in indexXX:
						if POSC[indexZ][indexY][indexX]:
							self.gridIndex[indexCount] = [indexX, indexY, indexZ]
							indexCount += 1
						# end if
					# end for
				# end for
			# end for
		# end if
	# end def __init__
# end class SequenceRectCenter

def getSequence(sequenceName,grid):
	"""
	Returns an instance of the Sequence object of requested sequenceName.
	:raise: a SequenceError if the Sequence is not supported.
	"""
	sequenceName = str(sequenceName)
	if sequenceName == "RectDirect":
		return SequenceRectDirect(grid)
	elif sequenceName == "RectCenter":
		return SequenceRectCenter(grid)
	raise SequenceError("Unsupported sequence (%s)." % sequenceName)

if __name__ == '__main__':
	p0 = [10.0,15.0,20.0]
	dirx = [1.0,0.0,0.0]
	diry = [0.0,1.0,0.0]
	dirz = [0.0,0.0,1.0]
	nx = 3
	ny = 3
	nz = 3
	myGrid = Grid(p0,dirx,diry,dirz,nx,ny,nz)
	myGrid.printGrid()
	mySeqRectDir = getSequence("RectDirect",myGrid)
	print('getDimensions: ', mySeqRectDir.getDimensions())
	print('gridSize: ', mySeqRectDir.gridSize)
	for i in range(nz):
		for j in range(ny):
##			msg = "N: {}".format(i*j*nz)
##			print(msg, end="")
			for k in range(nx):
				N = k + j*nx+i*ny*nx
				gridIndexes = mySeqRectDir.gridIndex[N]
				
				msg = "N: {}, i: {}, j: {}, k: {}, gridIndex: {}".format(N, k, j, i,gridIndexes)
				print(msg)
