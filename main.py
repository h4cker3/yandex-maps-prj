import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, )

from ui import Ui_MainWindow

GEOSEARCH_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def get_request(server: str, params: dict[str, str] = None):
    response = requests.get(server, params)
    if not response:
        print('Server is sad with status code', response.status_code)
        print(response.reason)
        print(response.text)
        return response
    return response


def geocoder_request(apikey: str, geocode: str, format: str = 'json'):
    API_SERVER = 'https://geocode-maps.yandex.ru/1.x/'
    params = {
        'apikey': apikey,
        'geocode': geocode,
        'format': format,
    }

    response = get_request(API_SERVER, params)
    json = response.json()
    return json["response"]["GeoObjectCollection"]["featureMember"][0][
        "GeoObject"]


def static_maps_request(*, center_point, org_point, scale, map_type):
    API_SERVER = 'https://static-maps.yandex.ru/1.x/'
    params = {
        'll': center_point,
        'z': scale,
        'l': map_type,
        "pt": "{0},pm2dgl".format(org_point)
    }
    response = get_request(API_SERVER, params)
    return response.content


def generate_image(*, center_point, org_point, scale, map_type):
    img_content = static_maps_request(
        center_point=center_point,
        org_point=org_point,
        map_type=map_type,
        scale=scale
    )
    with open('map.png', 'wb') as file:
        file.write(img_content)


class GeocodeFinder:
    def __init__(self):
        self.apikey = GEOSEARCH_API_KEY

    def get_ll_by_address(self, address):
        request = f"http://geocode-maps.yandex.ru/1.x/?apikey={self.apikey}&geocode={address}&lang=ru_RU&format=json&type=biz"

        response = requests.get(request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            return toponym_coodrinates.replace(' ', ',')

    def get_full_address(self, address):
        request = f"http://geocode-maps.yandex.ru/1.x/?apikey={self.apikey}&geocode={address}&lang=ru_RU&format=json&type=biz"

        response = requests.get(request)
        if response:
            json_response = response.json()

            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            return toponym_address


geofind = GeocodeFinder()


class MainApp(QMainWindow, Ui_MainWindow):
    BASE_SCALE = 12
    START_IMAGE_PATH = ''
    MAP_TYPE = {
        'Схема': 'map',
        'Спутник': 'sat',
        'Схема + Спутник': 'sat,skl'
    }
    KEYBOARD_KEYS = [
        Qt.Key_Left, Qt.Key_Right, Qt.Key_Down, Qt.Key_Up, Qt.Key_PageUp,
        Qt.Key_PageDown,
    ]

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Проект YANDEX MAPS API')
        self.scheme.nextCheckState()

        self.map_type = MainApp.MAP_TYPE['Схема']
        self.org_name = None
        self.center_point = None
        self.pixmap = QPixmap(self.START_IMAGE_PATH)
        self.scale = MainApp.BASE_SCALE

        self.buttonGroup.buttonClicked.connect(self.change_type_map)
        self.search.clicked.connect(self._search_btn_clicked)
        self.clear_btn.clicked.connect(self._clean_btn_clicked)
        self.show_image()
        self.search_bar.setText('Москва')

    def show_image(self):
        self.map.setPixmap(self.pixmap)

    def _search_btn_clicked(self):
        self.scale = MainApp.BASE_SCALE
        self.org_name = self.search_bar.text()
        self.org_point = geofind.get_ll_by_address(
            address=self.org_name
        )
        self.center_point = self.org_point
        self.take_picture()

    def _clean_btn_clicked(self):
        self.scale = MainApp.BASE_SCALE
        self.org_name = None
        self.search_bar.setText('')
        self.address.setText('')
        self.pixmap = QPixmap(self.START_IMAGE_PATH)
        self.show_image()

    def take_picture(self):
        generate_image(
            center_point=self.center_point,
            org_point=self.org_point,
            map_type=self.map_type,
            scale=self.scale,
        )
        self.pixmap = QPixmap('map.png')
        self.show_image()
        self.address.setText(self.get_full_address())

    def get_full_address(self):
        return geofind.get_full_address(
            address=self.org_name
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.scale += 1
        elif event.key() == Qt.Key_PageDown:
            self.scale -= 1
        elif event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Down, Qt.Key_Up]:
            self.update_center_point(event)

        if event.key() in MainApp.KEYBOARD_KEYS:
            self.scale_checker()
            self.take_picture()

    def update_center_point(self, event):
        longitude, latitude = [float(cord) for cord in
                               self.center_point.split(',')]
        if event.key() == Qt.Key_Left:
            if longitude - self.count_longitude() > -180:
                longitude -= self.count_longitude()
        if event.key() == Qt.Key_Right:
            if longitude + self.count_longitude() < 180:
                longitude += self.count_longitude()
        if event.key() == Qt.Key_Down:
            if latitude - self.count_latitude() > -90:
                latitude -= self.count_latitude()
        if event.key() == Qt.Key_Up:
            if latitude + self.count_latitude() < 90:
                latitude += self.count_latitude()
        self.center_point = f'{longitude},{latitude}'

    def scale_checker(self):
        self.scale = min(self.scale, 17)
        self.scale = max(self.scale, 1)

    def count_latitude(self):
        H = 450
        return 180 / (2 ** (self.scale + 8)) * H

    def count_longitude(self):
        W = 600
        return 360 / (2 ** (self.scale + 8)) * W

    def change_type_map(self):
        self.map_type = MainApp.MAP_TYPE[
            self.buttonGroup.checkedButton().text()]
        if self.org_name:
            self.take_picture()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainapp = MainApp()
    mainapp.show()
    sys.exit(app.exec())
