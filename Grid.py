#-------------------------------------------------------------------------------
# Name:        Grid
# Purpose:
#
# Author:      ED
#
# Created:     04/03/2017
# Copyright:   (c) ED 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from __future__ import print_function
import numpy as np

class GridError(Exception):

	"""GridError error"""
# end class GridError

class Grid (object):
	"""
	Describes the scanning grid.
	"""
	def __init__(self, p0, dirX, dirY, dirZ, NX=None, NY=None, NZ=None, lenghtX=None, lenghtY=None, lenghtZ=None):
		self.define(p0, dirX, dirY, dirZ, NX, NY, NZ, lenghtX, lenghtY, lenghtZ)
	# end def __init__


	def define(self, p0=None, dirX=None, dirY=None, dirZ=None, NX=None, NY=None, NZ=None, lenghtX=None, lenghtY=None, lenghtZ=None):
		if p0 is not None:
			self.p0 = np.array(p0)         #[x, y, z] Initial Position
		# end if
		if dirX is not None:
			self.dirX = np.array(dirX)     #[x, y, z] Vector pointing X direction
		# end if
		if dirY is not None:
			self.dirY = np.array(dirY)     #[x, y, z] Vector pointing X direction
		# end if
		if dirZ is not None:
			self.dirZ = np.array(dirZ)     #[x, y, z] Vector pointing X direction
		# end if

		if NX is not None:
			self.NX = NX
			self.lengthX= (self.NX -1) *self.getIncrementX()
		elif lenghtX is not None:
			self.lengthX = lenghtX
			self.NX = int(lenghtX/self.self.getIncrementX())
		else:
			raise GridError("Can not define number of elements in X direction")
		# end if

		if NY is not None:
			self.NY = NY
			self.lengthY= (self.NY -1) *self.getIncrementY()
		elif self.lengthY is not None:
			self.lengthY =self.lengthY
			self.NY = int(self.lengthY/self.self.getIncrementY())
		else:
			raise GridError("Can not define number of elements in Y direction")
		# end if

		if NZ is not None:
			self.NZ = NZ
			self.lengthZ= (self.NZ -1)*self.getIncrementZ()
		elif lenghtZ is not None:
			self.lengthZ = lenghtZ
			self.NZ = int(lenghtZ/self.self.getIncrementZ())
		else:
			raise GridError("Can not define number of elements in Z direction")
		# end if
		self.gridSize = self.NX * self.NY * self.NZ

		self.edges = np.zeros((8, 3))
		self.edges[0]=p0
		self.edges[1]=p0+float(self.NX)*self.dirX
		self.edges[2]=p0+float(self.NY)*self.dirY
		self.edges[3]=p0+float(self.NZ)*self.dirZ
		self.edges[4]=self.edges[1]+float(self.NY)*self.dirY
		self.edges[5]=self.edges[1]+float(self.NZ)*self.dirZ
		self.edges[6]=self.edges[2]+float(self.NZ)*self.dirZ
		self.edges[7]=self.edges[4]+float(self.NZ)*self.dirZ
	# end def define

	def defineTestGrid(self):
		self.p0 = np.array([10.0,15.0,20.0])
		self.dirX = np.array([1.0,0.0,0.0])
		self.dirY = np.array([0.0,1.0,0.0])
		self.dirZ = np.array([0.0,0.0,1.0])
		self.NX = 5
		self.NY = 5
		self.NZ = 5
	# end def defineTestGrid

	def printGrid(self):
		print('p0: [ {:.3f}, {:.3f}, {:.3f} ]'.format(self.p0[0],self.p0[1],self.p0[2]))
		print('dirX: [ {:.3f}, {:.3f}, {:.3f} ]'.format(self.dirX[0],self.dirX[1],self.dirX[2]))
		print('dirY: [ {:.3f}, {:.3f}, {:.3f} ]'.format(self.dirY[0],self.dirY[1],self.dirY[2]))
		print('dirZ: [ {:.3f}, {:.3f}, {:.3f} ]'.format(self.dirZ[0],self.dirZ[1],self.dirZ[2]))
		print('length: [ {:.3f}, {:.3f}, {:.3f} ]'.format(self.lengthX,self.lengthY,self.lengthZ))

		for i in range (8):
			print('edge[{}]: [ {:.3f}, {:.3f}, {:.3f} ]'.format(i,self.edges[i][0],self.edges[i][1],self.edges[i][2]))

	# end def defineTestGrid

	def getIncrementX(self):
		return np.sqrt((self.dirX**2).sum())
	# end def getIncrementX

	def getIncrementY(self):
		return np.sqrt((self.dirY**2).sum())
	# end def getIncrementY

	def getIncrementZ(self):
		return np.sqrt((self.dirZ**2).sum())
	# end def getIncrementZ

	def getPosition(self, nx, ny, nz):
		if nx > self.NX:
			raise GridError("Index X out of range")
		if ny > self.NY:
			raise GridError("Index Y out of range")
		if nz > self.NZ:
			raise GridError("Index Z out of range")
		return self.p0 + nx*self.dirX + ny*self.dirY + nz*self.dirZ
	# end def getPosition
# end class Grid

if __name__ == '__main__':
	p0 = [10.0,15.0,20.0]
	dirx = [1.0,0.0,0.0]
	diry = [0.0,1.0,0.0]
	dirz = [0.0,0.0,1.0]
	nx = 5
	ny = 5
	nz = 5
	myGrid = Grid(p0,dirx,diry,dirz,nx,ny,nz)
	myGrid.printGrid()
	print('gridSize: ',myGrid.gridSize)
	x,y,z = myGrid.getPosition(5,5,5)
	print('1, 2, 3: ',x,y,z)
