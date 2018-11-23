import sys

from PyQt5.QtWidgets import QApplication

from visualize import GLWindow

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = GLWindow()
	window.show()
	sys.exit(app.exec_())
