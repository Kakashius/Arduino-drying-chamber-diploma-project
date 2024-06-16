import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import QPushButton, QDialog, QLabel, QLineEdit, QFormLayout
from PyQt5.QtCore import Qt


class Dialog(QDialog):
    def __init__(self, *args):
        super(Dialog, self).__init__()
        self.temp, self.hum = args

        self.setWindowTitle("Ввод данных для этапа кондиционирования")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.setFixedSize(640, 480)

        layout = QFormLayout()  # Макет диалогового окна
        self.setLayout(layout)


        # Текст окна
        layout.addRow(QLabel("Введите отн. влажность суш. агента по диаграмме равновесной влажности древесины при:"))
        layout.addRow(QLabel(f"температуре суш. агента = {self.temp} °C"))
        layout.addRow(QLabel(f"равновесной влажности = {self.hum} %"))

        # Ввод
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setPlaceholderText("Например: 34")
        layout.addRow(self.lineEdit)

        # Кнопка Применить
        self.applyButton = QPushButton("Применить", self)
        self.applyButton.setEnabled(False)
        layout.addRow(self.applyButton)

        # Проверка на заполнение
        self.lineEdit.textChanged.connect(self.isTextInt)
        # Закрытие и отправка данных
        self.applyButton.clicked.connect(self.isApplyClicked)

    def isTextInt(self):
        text = self.lineEdit.text()
        self.applyButton.setEnabled(text.isdigit())

    def isApplyClicked(self):
        self.set_hum = self.lineEdit.text()  # Установка влажности кондиционирования
        self.accept()  # закрыть окно

    def closeEvent(self, event):  # Запрет закрытия диалогового окна
        if not self.result():
            event.ignore()