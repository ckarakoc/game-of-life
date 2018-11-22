import sys
import numpy as np
import OpenGL.GL as gl

from patterns import *
from life import GameOfLife
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QOpenGLWidget


# noinspection PyPep8Naming
class GLWindow(QOpenGLWidget):
	xRotationChanged = pyqtSignal(int)
	yRotationChanged = pyqtSignal(int)
	zRotationChanged = pyqtSignal(int)

	def __init__(self, parent=None):
		super(GLWindow, self).__init__(parent)

		inp = spaceship()
		pattern = np.array([[0 if j == '.' else 1 for j in i] for i in inp.split()])

		n = 6
		world = np.zeros((pattern.shape[0] + n, pattern.shape[1] + n), dtype=np.bool)
		world[int(n / 2):pattern.shape[0] + int(n / 2), int(n / 2):pattern.shape[1] + int(n / 2)] = pattern

		self.gol = GameOfLife(world)

		self.object = 0
		self.curr_gen = 0
		self.xRot = 0
		self.yRot = 0
		self.zRot = 0

		self.zoomFactor = 1.0
		self.leftToScreen = 1.0
		self.rightToScreen = 1.0

		self.minDepth = -0.8
		self.maxDepth = -1.0

		self.setFocusPolicy(Qt.WheelFocus)
		self.lastPos = QPoint()
		self.backgroundColor = QColor(0, 0, 0, 0)

	@staticmethod
	def getOpenglInfo():
		return f"""
			Vendor: {gl.glGetString(gl.GL_VENDOR)}
            Renderer: {gl.glGetString(gl.GL_RENDERER)}
            OpenGL Version: {gl.glGetString(gl.GL_VERSION)}
            Shader Version: {gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)}
		"""

	def initializeGL(self):
		print(self.getOpenglInfo())

		self.setClearColor(self.backgroundColor)
		self.object = self.makeObject()
		self.curr_gen = self.next_gen()
		gl.glShadeModel(gl.GL_FLAT)
		gl.glEnable(gl.GL_DEPTH_TEST)
		gl.glDisable(gl.GL_CULL_FACE)

	def makeObject(self):
		genList = gl.glGenLists(1)
		gl.glNewList(genList, gl.GL_COMPILE)

		minPoint = [-1, -1, self.minDepth]
		maxPoint = [1, 1, self.maxDepth]

		# The box and its sides
		gl.glLineWidth(4)
		self.setColor(QColor(64, 224, 208, 0))
		self.box(minPoint, maxPoint)

		self.setColor(QColor(64, 224, 208, 0).darker())

		gl.glBegin(gl.GL_QUADS)

		# up
		gl.glVertex3d(minPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3d(minPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3d(maxPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3d(maxPoint[0], minPoint[1], maxPoint[2])
		# down
		gl.glVertex3d(minPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3d(maxPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3d(maxPoint[0], maxPoint[1], minPoint[2])
		gl.glVertex3d(minPoint[0], maxPoint[1], minPoint[2])
		# right
		gl.glVertex3d(maxPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3d(maxPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3d(maxPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3d(maxPoint[0], maxPoint[1], minPoint[2])
		# left
		gl.glVertex3d(minPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3d(minPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3d(minPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3d(minPoint[0], maxPoint[1], minPoint[2])

		gl.glEnd()

		xshape = (2.0 / self.gol.world.shape[0])
		yshape = (2.0 / self.gol.world.shape[1])

		self.setColor(QColor(64, 224, 208, 0))
		for x, row in enumerate(self.gol.world):
			for y, col in enumerate(row):
				minPoint = [x * xshape - 1, y * yshape - 1, self.minDepth]
				maxPoint = [x * xshape - 1 + xshape, y * yshape - 1 + yshape, self.maxDepth]
				self.box(minPoint, maxPoint)
		gl.glEndList()

		return genList

	def minimumSizeHint(self):
		return QSize(50, 50)

	def sizeHint(self):
		return QSize(800, 800)

	def setXRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.xRot:
			self.xRot = angle
			self.xRotationChanged.emit(angle)
			self.update()

	def setYRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.yRot:
			self.yRot = angle
			self.yRotationChanged.emit(angle)
			self.update()

	def setZRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.zRot:
			self.zRot = angle
			self.zRotationChanged.emit(angle)
			self.update()

	def paintGL(self):
		gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
		gl.glLoadIdentity()
		gl.glTranslated(0.0, 0.0, -10.0)
		gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
		gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
		gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
		ortho = np.multiply(np.array((-2, +2, -2, +2), dtype=float), self.zoomFactor)
		# gl.glMatrixMode(gl.GL_PROJECTION)
		# gl.glLoadIdentity()
		gl.glOrtho(ortho[0], ortho[1], ortho[2], ortho[3], 4.0, 15.0)
		# gl.glMatrixMode(gl.GL_MODELVIEW)
		gl.glCallList(self.object)
		gl.glCallList(self.curr_gen)

	def resizeGL(self, width, height):
		gl.glViewport(0, 0, width, height)
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glLoadIdentity()
		gl.glOrtho(-2 * (width / height), +2 * (width / height), -2, +2, 4.0, 15.0)
		gl.glMatrixMode(gl.GL_MODELVIEW)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.close()
		elif event.key() == Qt.Key_N:
			self.gol.next_generation()
			self.curr_gen = self.next_gen()
			self.update()

	def mousePressEvent(self, event):
		self.lastPos = event.pos()
		print(f"Mouse Pressed at location {self.lastPos}")

	def mouseMoveEvent(self, event):
		dx = event.x() - self.lastPos.x()
		dy = event.y() - self.lastPos.y()

		if event.buttons() == Qt.LeftButton:
			self.setXRotation(self.xRot + 8 * dy)
			self.setYRotation(self.yRot + 8 * dx)
		elif event.buttons() == Qt.RightButton:
			self.setXRotation(self.xRot + 8 * dy)
			self.setZRotation(self.zRot + 8 * dx)

		self.lastPos = event.pos()

	def wheelEvent(self, event):
		"""http://doc.qt.io/qt-5/qwheelevent.html"""
		scroll = event.angleDelta()
		if scroll.y() > 0:  # up
			self.zoomFactor -= 0.1
			self.update()
		else:  # down
			self.zoomFactor += 0.1
			self.update()

	@staticmethod
	def box(minPoint, maxPoint):
		gl.glBegin(gl.GL_LINES)
		gl.glVertex3f(minPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3f(maxPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], maxPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], minPoint[1], maxPoint[2])

		gl.glVertex3f(maxPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3f(minPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], maxPoint[1], minPoint[2])

		gl.glVertex3f(maxPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3f(maxPoint[0], maxPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], maxPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3f(minPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], minPoint[1], maxPoint[2])

		gl.glVertex3f(minPoint[0], maxPoint[1], maxPoint[2])
		gl.glVertex3f(minPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], minPoint[1], maxPoint[2])
		gl.glVertex3f(maxPoint[0], minPoint[1], minPoint[2])
		gl.glVertex3f(maxPoint[0], maxPoint[1], minPoint[2])
		gl.glVertex3f(minPoint[0], maxPoint[1], minPoint[2])
		gl.glEnd()

	@staticmethod
	def quad(x1, y1, x2, y2, x3, y3, x4, y4, z1, z2):
		gl.glVertex3d(x1, y1, z1)
		gl.glVertex3d(x2, y2, z1)
		gl.glVertex3d(x3, y3, z1)
		gl.glVertex3d(x4, y4, z1)

		gl.glVertex3d(x4, y4, z2)
		gl.glVertex3d(x3, y3, z2)
		gl.glVertex3d(x2, y2, z2)
		gl.glVertex3d(x1, y1, z2)

	def next_gen(self):
		genList = gl.glGenLists(1)
		gl.glNewList(genList, gl.GL_COMPILE)

		xshape = (2.0 / self.gol.world.shape[0])
		yshape = (2.0 / self.gol.world.shape[1])

		gl.glBegin(gl.GL_QUADS)
		for x, row in enumerate(self.gol.world):
			for y, alive in enumerate(row):
				minPoint = [x * xshape - 1, y * yshape - 1, self.minDepth]
				maxPoint = [x * xshape - 1 + xshape, y * yshape - 1 + yshape, self.maxDepth]
				if alive:
					self.setColor(QColor(119, 136, 153, 0))
				else:
					self.setColor(QColor(47, 79, 79, 0))
				self.quad(minPoint[0], minPoint[1], minPoint[0], maxPoint[1], maxPoint[0], maxPoint[1], maxPoint[0], minPoint[1], minPoint[2], maxPoint[2])

		gl.glEnd()
		gl.glEndList()

		return genList

	def normalizeAngle(self, angle):
		while angle < 0:
			angle += 360 * 16
		while angle > 360 * 16:
			angle -= 360 * 16
		return angle

	def setClearColor(self, c):
		gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

	def setColor(self, c):
		gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = GLWindow()
	window.show()
	sys.exit(app.exec_())
