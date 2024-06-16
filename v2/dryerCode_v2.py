import os
from os import path
import sys
import pyqtgraph as pg  # Библиотека графиков
from PyQt6 import uic   # Конвентирование .ui в .py
from PyQt6.QtWidgets import QMainWindow, QStatusBar   # Окно, статус-бар
from PyQt6.QtCore import QIODevice, QTimer  # Связы устройств, таймер
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo # Обработчик данных Serial, список портов

from PyQt6.QtWidgets import QApplication    # Подключение пакет приложения

from Trees import Tree
from dialogWindow import Dialog

class DryerApp(QMainWindow):
    def __init__(self):
        super(DryerApp, self).__init__()

        # self.pathToExe = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
        # self.pathToUi = path.abspath(path.join(self.pathToExe, 'interface_v2.ui'))
        # uic.loadUi(self.pathToUi, self)
        uic.loadUi('interface_v2.ui', self)    # Загрузка интерфейса   !!!
        self.setWindowTitle("Управление сушильной камерой") # Установка названия

        self.status = QStatusBar()  # Установка статус-бара
        self.setStatusBar(self.status)

        self.connectSerial = QSerialPort()  # Устанавка связи по Serial
        self.connectSerial.setBaudRate(115200)  # Скорость чтения/записи\

        self.timer = QTimer()  # Инициализация таймера
        self.timer.setInterval(1000)    # Интервал - 1 секунда
        self.timer.start()  # Запуск таймера


        self.statusMessage = {
            "Порт:": "Не выбран",
            "Связь:": "Не установлена"
        }


        self.styles = {"color": "white", "font-size": "18px"}  # Настройка графиков
        self.graphTemp.setLabel("left", "Температура, °C", **self.styles)
        self.graphTemp.setLabel("bottom", "Время, сек", **self.styles)
        self.graphHumid.setLabel("left", "Влажность, %", **self.styles)
        self.graphHumid.setLabel("bottom", "Время, сек", **self.styles)
        self.graphTemp.showGrid(x=True, y=True)
        self.graphHumid.showGrid(x=True, y=True)

        self.tempTime = list(range(10))  # Хранение данных графика температуры
        self.tempList = list(0 for _ in range(10))
        self.tempSetList = list(0 for _ in range(10))
        self.humidTime = list(range(10))  # Хранение данных графика температуры
        self.humidList = list(0 for _ in range(10))
        self.humidSetList = list(0 for _ in range(10))

        self.treeBox.addItems(list(Tree.treeList.keys()))  # Выбор породы и режима сушки
        self.treeMode.addItems(Tree.treeList[self.treeBox.currentText()])
        self.treeBox.currentIndexChanged.connect(self.treeChanged)

        self.setTreeSize.textChanged.connect(lambda: self.canDry(self.setTreeSize.text()))  # Изменение настроек сушки
        self.setTreeWidth.textChanged.connect(lambda: self.canDry(self.setTreeWidth.text()))
        self.setStartHum.textChanged.connect(lambda: self.canDry(self.setStartHum.text()))
        self.setTreeHum.textChanged.connect(lambda: self.canDry(self.setTreeHum.text()))

        self.status.showMessage(self.sendStatusBar(self.statusMessage))
        self.disconnectButton.setEnabled(False)
        self.setPorts() #Инициализация доступных портов
        self.portList.currentTextChanged.connect(lambda: self.connectButton.setEnabled(True))
        self.connectButton.clicked.connect(self.openPort)   # Подключить порт чтения/записи
        self.disconnectButton.clicked.connect(self.closePort)  # Отключить порт чтения/записи

        self.connectSerial.readyRead.connect(self.fromPort)  # Чтение с Arduino

        self.viewParameters.setEnabled(False)
        self.dials.setEnabled(False)
        self.autoMode.toggled.connect(self.autoSettings)    #Режимы регулирования параметров
        self.manualMode.toggled.connect(self.manualSettings)

        # ОСНОВНОЙ ПРОЦЕСС
        self.dryStart.clicked.connect(self.startDrying) # Начать процесс сушки
        self.dryStop.clicked.connect(self.stopDrying) # Остановить процесс сушки


        self.show()

    def startDrying(self):  # Начать процесс сушки
        if not all((self.setTreeSize.text(), self.setTreeWidth.text(),self.setStartHum.text(), self.setTreeHum.text())):
            return
        self.dryStart.setEnabled(False)
        self.dryStop.setEnabled(True)
        treeDry = Tree(self.treeBox.currentText(),
                          self.treeMode.currentText(),
                          self.setTreeSize.text(),
                          self.setTreeWidth.text(),
                          self.setStartHum.text(),
                          self.setTreeHum.text())
        
        startWindow = Dialog(*treeDry.show_to_window)
        startWindow.exec_()

        with open("const_tree_parameters.txt", "w") as file:    # Отправка неизменяемых параметров в файл
            for parameter in treeDry.constant_file_parameters:
                file.write(f"{parameter}\n")

        with open("stages.txt", "w") as file:   # Отправка этапов в файл
            for stage in treeDry.stages_file:
                file.write(f"{stage}\n")

        for stage_data in treeDry.execute_proccess(startWindow.set_hum):    # Отправка данных на Arduino
            self.sendToPort(stage_data)


    def stopDrying(self):   # Остановить процесс сушки  !!!!!
        self.dryStop.setEnabled(False)
        self.dryStart.setEnabled(True)
        self.sendToPort(Tree.stop())
        if path.exists("const_tree_parameters.txt"):    #Удаляет файл изменяемых параметров, если нажата кнопка Стоп
            os.remove("const_tree_parameters.txt")
        if path.exists("stages.txt"):    #Удаляет файл этапов
            os.remove("stages.txt")

    def treeChanged(self):  # Выбор режима сушки
        self.treeMode.clear()
        self.treeMode.addItems(Tree.treeList[self.treeBox.currentText()])

    def canDry(self, lineText): # Изменение настроек сушки перед началом
        try:
            if lineText != "":
                float(lineText)
                self.dryStart.setEnabled(True)
            else:
                self.dryStart.setEnabled(False)
        except ValueError:
            self.dryStart.setEnabled(False)

    def autoSettings(self): # Автоматическая регулирование !!!!!
        self.dials.setEnabled(False)
        self.sendToPort(["2", "0", "0", "0"])

    def manualSettings(self):   # Ручное регулирование !!!!!!
        self.dials.setEnabled(True)
        self.tempDial.valueChanged.connect(self.manualTempChange)  # Меняет установку температуры вручную
        self.humDial.valueChanged.connect(self.manualHumChange)  # Меняет установку влажности вручную
        self.sendToPort(["2", "1", str(self.tempDial.value()), str(self.humDial.value())])  # Ручная отправка

    def manualTempChange(self, val): # Меняет установку температуры вручную
        self.tempDialSet.setText(str(val))
        self.tempSet_lbl.setText(str(val) + " ℃")
        pass
    def manualHumChange(self, val):  # Меняет установку влажности вручную
        self.humDialSet.setText(str(val))
        self.humSet_lbl.setText(str(val) + " %")
        pass

    def setPorts(self): #Инициализация доступных портов
        ports = []
        ports.clear()
        for port in QSerialPortInfo().availablePorts(): # Получить список портов
            ports.append(port.portName())
        self.portList.clear()
        self.portList.addItems(ports)   # Доступные порты в комбо-бокс

    def openPort(self): # Подключить порт чтения/записи
        portName = self.portList.currentText()
        self.statusMessage["Порт:"] = portName    # Задать порт в статус-бар
        self.status.showMessage(self.sendStatusBar(self.statusMessage))
        self.connectSerial.setPortName(portName)  # Задать порт для соединения
        self.connectSerial.open(QIODevice.ReadWrite)  # Открыть порт для чтения и записи
        self.connectButton.setEnabled(False)  # Закрыть доступ к кнопке Подключить
        self.portList.setEnabled(False)  # Закрыть доступ к выбору порта
        self.disconnectButton.setEnabled(True)  # Открыть доступ к кнопке Отключить
        self.viewParameters.setEnabled(True)
        self.DryParameters.setEnabled(True)

    def closePort(self): # Отключить порт чтения/записи
        self.connectSerial.close()
        self.statusMessage["Порт:"] = "Не выбран"
        self.statusMessage["Связь:"] = "Не установлена"
        self.status.showMessage(self.sendStatusBar(self.statusMessage))
        self.portList.setEnabled(True)  # Открыть доступ к выбору порта
        self.connectButton.setEnabled(True)  # Открыть доступ к кнопке Подключить
        self.disconnectButton.setEnabled(False)  # Закрыть доступ к кнопке Отключить
        self.viewParameters.setEnabled(False)
        self.DryParameters.setEnabled(False)

    def sendStatusBar(self, message):   #Отправка в статус-бар
        return "    ".join("{0} {1}".format(key, value) for key, value in message.items())


    def fromPort(self): # Чтение с Arduino
        if not self.connectSerial.canReadLine():  # Выход, если нет связи
            self.statusMessage["Связь:"] = "Не установлена"
            self.status.showMessage(self.sendStatusBar(self.statusMessage))
            return
        self.statusMessage["Связь:"] = "Установлена"
        self.status.showMessage(self.sendStatusBar(self.statusMessage))
        readFromPort = str(self.connectSerial.readLine(), "utf-8")  # Чтение данных (str)

        readFromPort.strip()
        self.parcingFromPort(readFromPort.split(","))  # Парсинг данных с Arduino   !!!!!!!!!

        self.const_labels = []
        if path.exists("const_tree_parameters.txt"):
            with open("const_tree_parameters.txt", "r") as file:
                self.const_labels = file.readlines()
            self.setStartHum_lbl.setText(self.const_labels[0].strip() + "%")
            self.treeHumSet_lbl.setText(self.const_labels[1].strip() + "%")
            self.categorySet_lbl.setText(self.const_labels[2].strip())
            self.treeType_lbl.setText(self.const_labels[3].strip())
            self.sizeXwidth_lbl.setText(self.const_labels[4].strip() + "мм")
            self.treeMode_lbl.setText(self.const_labels[5].strip())

        self.stage_label = []   # Храним этапы сушки
        if path.exists("stages.txt"):
            with open("stages.txt", "r") as file:
                self.stage_label = [i.strip() for i in file.readlines()]

    def parcingFromPort(self, data):    # Парсинг данных с Arduino  !!!!!!!!!!!!
        if data[0] == "1":
            self.totalTimer_lbl.setText(self.time_left(int(data[1])))   # Таймер
        if data[0] == "2":
            self. ventSpeed_lbl.setText(data[1] + " м/с")  # Скорость вентилятора
            self.valve_lbl.setText(("Нет", "Да")[int(data[2])]) # Состояние увлажненмя
            self.hum_lbl.setText(data[3] + "%")    # Текущая влажность
            self.humSet_lbl.setText(data[4] + "%") # Установленная влажность
            #
            #
            self.timer.timeout.connect(lambda: self.himidityPlot(float(data[3]), float(data[4])))   # График влажности
        if data[0] == "3":
            self.temp_lbl.setText(data[1] + "°C")  # Текущая темппературв
            self.tempSet_lbl.setText(data[2] + "°C")   # Установленная температура
            self.step_lbl.setText(self.stage_label[int(data[3])])   # Этап сушки
            #
            #
            self.timer.timeout.connect(lambda: self.temperaturePlot(float(data[1]), float(data[2])))    #График температуры
        if data[0] == "4":
            self.treeHum_lbl.setText(data[1] + "%")


    def time_left(self, time):  # Таймер процесса сушки
        if time <= 0:
            return "Сушка завершена!"
        hrs, secs = divmod(time, 3600)
        mins, secs = divmod(secs, 60)
        return f"{hrs:02}:{mins:02}:{secs:02}"

    def sendToPort(self, data): # Парсинг и отправка в Arduino
        sendData = ""
        for val in data:
            sendData += str(int(val)) + ","
        sendData = sendData[:-1]  # Удаляем последнюю запятую
        sendData += ";"  # Добавляем терминатор ;
        print(sendData)
        self.connectSerial.write(sendData.encode())  # Отправляем массив байтов В порт

    def temperaturePlot(self, valueTemperature, setTemperature):  # График температуры
        self.graphTemp.clear()
        del self.tempTime[0]
        self.tempTime.append(self.tempTime[-1] + 1)
        del self.tempList[0]
        self.tempList.append(valueTemperature)
        del self.tempSetList[0]
        self.tempSetList.append(setTemperature)
        self.graphTemp.plot(self.tempTime, self.tempList, pen="g")
        self.graphTemp.plot(self.tempTime, self.tempSetList, pen="r")

    def himidityPlot(self, valueHumid, setHumid):  # График влажности
        self.graphHumid.clear()
        del self.humidTime[0]
        self.humidTime.append(self.humidTime[-1] + 1)
        del self.humidList[0]
        self.humidList.append(valueHumid)
        del self.humidSetList[0]
        self.humidSetList.append(setHumid)
        self.graphHumid.plot(self.humidTime, self.humidList, pen="g")
        self.graphHumid.plot(self.humidTime, self.humidSetList, pen="r")




app = QApplication(sys.argv)
interface = DryerApp()
sys.exit(app.exec_())  # Если система упадет, приложение прекратит работу
