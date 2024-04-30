import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QSize, QPoint, QEvent, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5 import QtCore


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Яндекс Карты")
        self.setGeometry(100, 100, 800, 600)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        self.load_map(55.751244, 37.618423, 12)

    def load_map(self, lat, lon, zoom):
        url = f"https://yandex.ru/maps/?ll={lat},{lon}&z={zoom}"
        self.web_view.load(QtCore.QUrl(url))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.zoom_in()
        elif event.key() == Qt.Key_PageDown:
            self.zoom_out()
        elif event.key() == Qt.Key_Up:
            self.move_up()
        elif event.key() == Qt.Key_Down:
            self.move_down()
        elif event.key() == Qt.Key_Left:
            self.move_left()
        elif event.key() == Qt.Key_Right:
            self.move_right()
        else:
            super().keyPressEvent(event)

    def zoom_in(self):
        self.web_view.page().runJavaScript(f"ymaps.map.setZoom(ymaps.map.getZoom() + 1)")

    def zoom_out(self):
        self.web_view.page().runJavaScript(f"ymaps.map.setZoom(ymaps.map.getZoom() - 1)")

    def move_up(self):
        self.move_map(0, -self.get_screen_size())

    def move_down(self):
        self.move_map(0, self.get_screen_size())

    def move_left(self):
        self.move_map(-self.get_screen_size(), 0)

    def move_right(self):
        self.move_map(self.get_screen_size(), 0)

    def move_map(self, dx, dy):
        js = f"ymaps.map.panBy({dx}, {dy}, {{duration: 0}});"
        self.web_view.page().runJavaScript(js)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
