//Инициализация библиотек, объектов, констант, хранилищ данных, системных таймеров
double tree_resist = 1;  // Сопротивление абсолютно сухой древесины (Ом)
int total_time = 0; //Общее время в секундах

int control_settings[3];  //Хранилище параметров регулирования: Авто ручной режимы

int temperatures[9];  //Хранение параметров температуры по этапам
int humids[9];  //Хранение параметров влажности по этапам
int vent_speeds[9]; //Хранение параметров скорости вентиляторов по этапам
unsigned long timers[9]; //Хранение параметров времени по этапам в миллисекундах
bool heat_pwr[9]; //Хранение параметров питания нагревателя по этапам
bool vent_pwr[9]; //Хранение параметров питания вентилятора по этапам
bool servo_pwr[9]; //Хранение параметров питания окон по этапам
bool valve_pwr[9]; //Хранение параметров питания увлажнения по этапам
int set_index = 0;  //Индекс текущего этапа
int length_params = 0; //Длина массива параметров

//Таймеры: дисплей, влажность древесины, температура, влажность суш. агента, клапан увл. системы, вентиляторы, продолжительность
uint32_t displayTmr, treeTmr, tempTmr, humidTmr, valveTmr, ventTmr, time_leftTimr;  

int treeHumid;  //Влажность древесины
int ventSpeed;  //Суммарная скорость вращения вентилятора
bool auto_Mode = 0; //Автоматический режим: 0, Ручной режим: 1
bool startCooling = 0; //Флаг возможности охлаждения камеры

bool canDry = 1;  //Флаг возможности сушки

int stage_index = 0;  //Индекс параметра текущего этапа
uint32_t stageTime; //Таймер текущего этапа

#include "LiquidCrystal_I2C.h"  //Библиотека управления дисплеем
LiquidCrystal_I2C lcd(0x27,16,2); //Объект дисплея - пин: А4, А5

#include "Servo.h"  //Библиотека управления сервоприводами
Servo servo;  //Объект сервоприводв
#define SERVO 8 //Пин 8

#include "DHT.h"  //Библиотека датчиков температуры и влажности
DHT sensor1(2, DHT11);  //Объект датчика №1, пин 2
DHT sensor2(3, DHT11);  //Объект датчика №1, пин 3

#define RELAY 11  //Объект нагревателя (реле), пин 11
bool relayON = true;  //Включить реле
bool relayFlag = false; //Флаг состояния реле
int period = 1000;  //Период реле
int activePeriod = 0; //Длительность импульса

#define VALVE 13 //Объект увлажнительной системы, пин 13
#define OUT_PIN A0  //Аналоговый пин измерения напряжения
#define IN_PIN 13 //Цифровой пин подачи напряжения

#define FORWARD_VENT 9  // Вентиляторы прямого вращения, Пины: 4, 5, 9
#define F_MC1 5
#define F_MC2 4

#define REVERSE_VENT 10  // Вентиляторы реверсивного вращения, Пины: 6, 7, 10
#define R_MC1 7
#define R_MC2 6

#include "GParser.h" //Библиотека парсинга данных с ПК
#include "AsyncStream.h"  //Библиотека ассинхронного чтения данных с ПК
AsyncStream<50> stream(&Serial, ";");  //Объект обработчика данных Serial, размер буфера: 50, терминатор: ";"

#include "PID_v1.h" //Библиотека ПИД-регулирования
double tempInput, tempOutput, tempSetpoint; //Переменные темп. регулироваия: вх. значение, вых. значение (сигнал), установка
double tKp = 40, tKi = 0.05, tKd = 0;  //Коэффициенты регулятора температуры
PID tempRegulator(&tempInput, &tempOutput, &tempSetpoint, tKp, tKi, tKd, DIRECT); //Объект регулирования температуры
double humidInput, humidOutput, humidSetpoint; //Переменные влаж. регулироваия: вх. значение, вых. значение (сигнал), установка
double hKp = 10, hKi = 0.0, hKd = 0.0; //Коэффициенты регулятора влажности
PID humidRegulator(&humidInput, &humidOutput, &humidSetpoint, hKp, hKi, hKd, REVERSE);  //Объект регулирования влажности

void setup() {  //Инициализация работы
  sensor1.begin();
  sensor2.begin();
  Serial.begin(115200); //Инициализация монитора порта
  Serial.flush();
  tempSetpoint = 0; //Установка температуры по умолчанию
  humidSetpoint = 0;  //Установка влажности по умолчанию
  tempRegulator.SetMode(AUTOMATIC); //Вкл. работы ПИД-регулирования температуры
  tempRegulator.SetOutputLimits(0, 255);  //Установить лимит вых.значений для регулирования температуры
  tempRegulator.SetSampleTime(1000);  //Установить период обработки регулирования температуры
  humidRegulator.SetMode(AUTOMATIC);  //Вкл. работы ПИД-регулирования влажности
  humidRegulator.SetOutputLimits(0, 90);  //Установить лимит вых.значений для регулирования температуры
  humidRegulator.SetSampleTime(50); //Установить период обработки регулирования влажности

  servo.attach(SERVO); //Установка пина на сервоприводы

  lcd.init(); //Инициализация работы дисплея
  lcd.backlight();

  pinMode(VALVE, OUTPUT); //Сконфигурировать пины
  pinMode(IN_PIN, OUTPUT);
  digitalWrite(IN_PIN, HIGH); //Подаем нарпяжение на древесину
  pinMode(RELAY, OUTPUT);
  digitalWrite(RELAY, !relayON);  //Выключаем реле при инициализации
  setPWM(0);
  pinMode(FORWARD_VENT, OUTPUT);  //Конфигурация пинов прямого вращения
  pinMode(F_MC1, OUTPUT);
  pinMode(F_MC2, OUTPUT);
  pinMode(REVERSE_VENT, OUTPUT);  //Конфигурация пинов прямого вращения
  pinMode(R_MC1, OUTPUT);
  pinMode(R_MC2, OUTPUT);
  forwardBrake();  //Останавливаем вентиляторы при инициализации
  reverseBrake();

  delay(500);
}

void loop() { //Цикл выполнения программы
  parcing();
  if (stage_index < length_params) {    //Пока выплняются этапы
    if (stage_index != 0 && timers[stage_index] == 0) {     //Для этапов без времени
      if (!startCooling && (tempInput >= tempInput)) { //Если таймер без указания времени этапа (Прогрев)
        stage_index++;  //Как выполнится прогрев - переход на следующий этап
        startCooling = 1; //Открыта возможность охлаждения камеры
      } else if(startCooling && (tempInput < tempSetpoint)) {  //Если таймер без указания времени этапа (Охлаждение)
        canDry = 0;
      } else {
        main_proccess();  //Выполняем управление на прогрев или охлаждение
      }
      if (stage_index < length_params) {
          stageTime = millis(); //Отмеряем время на текущий этап
        }
    } else {  //Время для остальных этапов
      if (millis() - stageTime >= timers[stage_index]) {  //Переход на следующий этап
        stage_index++;
        if (stage_index < length_params) {
          stageTime = millis(); //Отмеряем время на текущий этап
        }
      } else {
        main_proccess();  //Выполняем управление на текущий этап
      }
    }
  }
}
void main_proccess() {  //Выполнение программы
  if (canDry == 1) {      //Флаг возможности сушки
    change_parameters();  //Авто, ручная настройка 
    humidRegulation();    //Регулирование приточно-вытяжных каналов
    tempRegulation();     //Регулирование нагревательного элемента
    ventRegulation();     //Регулирование вентиляционной системы
    valveRegulation();    //Регулирование увлажнительной системы (клапан)
    lcdDisplay();         //Работа дисплея
    treeHumidity();       //Определение влажности древесины
    remaining_time();     //Определение оставшегося времени
  } else {
    setPWM(0);
    servo.write(0);
    digitalWrite(VALVE, LOW);
    forwardBrake();
    reverseBrake();
  }
}

void parcing() {  //Парсинг данных с ПК
  if (stream.available()) {
    GParser data(stream.buf, ","); //Отправка модулю данные в буфер с разделителем ","
    data.split(); //Разбивка данных
    switch (data.getInt(0)) {
      case 0: //Отключение системы регулирования: нагрев, вентилятор, окна, увлажнение
        canDry = 0; //Останавливаем работу
        set_index = 0;  //Обнуление индекса заполнения
        length_params = 1;  //Обнуление длины массива параметров
        startCooling = 0; //Обннуление флага возможности охлаждения
        break;
      case 1: //Установка неизменяемых данных, инициализация процесса
        tree_resist = data.getInt(1); //Сопротивление сухой древесины
        total_time = data.getFloat(2);  //Продолжительность сушки (в секундах)
        stage_index = 0;
        length_params = 1;
        canDry = 1;
        break;
      case 2: //Установка параметров регулирования
        control_settings[0] = data.getInt(1); // Утановка режима регулирования
        control_settings[1] = data.getInt(2); // Ручная установка температуры
        control_settings[2] = data.getInt(3); // Ручная установка температуры
        break;
      case 3:
        temperatures[set_index] = data.getInt(1);  //Параметр температуры по этапу
        humids[set_index] = data.getInt(2);  //Параметр влажности по этапу
        vent_speeds[set_index] = data.getInt(3); //Параметр скорости вентиляторов по этапу
        timers[set_index] = (unsigned long) (data.getFloat(4) * 3600000); //Параметр времени по этапу (в миллисекундах)
        heat_pwr[set_index] = data.getInt(5); //Параметр питания нагревателя по этапу
        vent_pwr[set_index] = data.getInt(6); //Параметр питания вентилятора по этапу
        servo_pwr[set_index] = data.getInt(7); //Параметр питания окон по этапу
        valve_pwr[set_index] = data.getInt(8);  //Параметр питания увлажнения по этапам
        set_index++;  // Изменение индекса массивов параметров
        length_params++;  //Динамическая длина массивов параметров
        break;
    }
  }
}

void lcdDisplay() { //Работа дисплея
  if (millis() - displayTmr >= 1000) {
    displayTmr = millis();
    lcd.clear();
    
    lcd.setCursor(0, 0);
    lcd.print("Temp.: ");
    lcd.print((int) tempInput);
    lcd.print(" ");
    lcd.print((char) 223);
    lcd.print("C");

    lcd.setCursor(0,1);
    lcd.print("Humid.: ");
    lcd.print((int) humidInput);
    lcd.print(" ");
    lcd.print("%");
  }
}

void treeHumidity() { //Определение влажности древесины
  if (millis() - treeTmr >= 600000) {
    double measuredVoltage = analogRead(OUT_PIN) * (5.0 / 1023.0); //Преобразование аналог. сигнала в напряжение
    double curentResist = (5.0 * 10000.0 / measuredVoltage) - 10000.0; //Теущее сопротивление древесины
    treeHumid = (1 - (curentResist / tree_resist)) * 100;  //Влажность древесины
    double packet[1];
    packet[0] = treeHumid;
    sendPacket(4, packet, 1);
  }
}
double averageVal(double val1 = 0.0, double val2 = 0.0) {  //Среднее значение
  if (isnan(val1)) {
    val1 = 0.0;
  }
  if (isnan(val2)) {
    val2 = 0.0;Ф
  }
  return (val1 + val2) / 2;
}

void setPWM(byte pwmSignal) { //Алгоритм управления реле
  activePeriod = (long)pwmSignal * period / 255;
  switch (pwmSignal) {
    case 0:
      digitalWrite(RELAY, !relayON);  //Выключаем реле
      break;
    case 255:
      digitalWrite(RELAY, relayON);  //Включаем на полную мощность
      break;
    default:
      if (millis() - tempTmr >= (relayFlag ? activePeriod : (period - activePeriod))) {
        relayFlag = !relayFlag;
        digitalWrite(RELAY, relayFlag ^ !relayON);
      }
      break;
  }
}

void tempRegulation() {  //Регулирование нагрева камеры
  if (heat_pwr[stage_index]) {
    if (millis() - tempTmr >= 1000) {
      tempTmr = millis();
      tempInput = averageVal(sensor1.readTemperature(), sensor2.readTemperature());
      tempRegulator.Compute();
      setPWM((int)tempOutput);

      double packet[3];
      packet[0] = tempInput;
      packet[1] = tempSetpoint;
      packet[3] = stage_index;
      sendPacket(3, packet, 3);
    }
  } else {  //Если питание на нагреватель выключено
    setPWM(0);
  }
}

void humidRegulation() {  // Регулирование влажности сушильного агента
  if (servo_pwr[stage_index]) {
    if (millis() - humidTmr >= 50) {  //Если окна включены
      humidTmr = millis();
      humidInput = averageVal(sensor1.readHumidity(), sensor2.readHumidity());
      humidRegulator.Compute();
      servo.write((int) humidOutput); //Управление окнами (сервоприводами)

      int stage_speed = map(vent_speeds[stage_index], 0, 4, 0, 255); //Скорость вентилятора от этапа
      int servo_signal = map((int) humidOutput, 0, 90, 0, 255); //Скорость вентилятора от влажности
      ventSpeed = constrain(stage_speed + servo_signal, 0, 255);

      double packet[4];
      packet[0] = map(ventSpeed, 0, 255, 0, 4);
      packet[1] = digitalRead(VALVE);
      packet[2] = humidInput;
      packet[3] = humidSetpoint;
      sendPacket(2, packet, 4);
    }  
  } else { // Если окна выключены
    servo.write(0);
    ventSpeed = 0;
  }
}

void valveRegulation() {  //Регулирование увлажнительной системы
  if (!valve_pwr[stage_index]) {
    digitalWrite(VALVE, LOW); //Закрыть клапан, если нет питания
  } else if (humidInput < humidSetpoint) {
    digitalWrite(VALVE, HIGH); //Открыть клапан
    if (millis() - valveTmr >= 15000) {
      valveTmr = millis();
      digitalWrite(VALVE, LOW); //Закрыть клапан
    }
  } else {
    digitalWrite(VALVE, LOW);
  }
}

void ventRegulation() { //Регулирование направления и скорости вентилятора
  if (vent_pwr[stage_index]) {
    if (millis() - ventTmr >= 30000) {
      ventTmr = millis();
      if (sensor2.readHumidity() >= sensor1.readHumidity()) {
        forwardBrake();
        startReverse(ventSpeed);  //Скорость вращениия
      } else {
        reverseBrake();
        startForward(ventSpeed);  //Скорость вращения
      }
    }
  } else {  //Если нет питания, отключаем вентиляторы
      forwardBrake();
      reverseBrake();
    }
}

void forwardBrake() {  //остановка вентиляторов прямого вращения
  digitalWrite(FORWARD_VENT, LOW);
  digitalWrite(F_MC1, LOW);
  digitalWrite(F_MC2, LOW);
  digitalWrite(FORWARD_VENT, HIGH);
}
void reverseBrake() {  //Остановка вентиляторов реверсивного вращения
  digitalWrite(REVERSE_VENT, LOW);
  digitalWrite(R_MC1, LOW);
  digitalWrite(R_MC2, LOW);
  digitalWrite(REVERSE_VENT, HIGH);
}
void startForward(int speed) {  //Скорость вращения вентиляторов прямого направления
  digitalWrite(FORWARD_VENT, LOW);
  digitalWrite(F_MC1, HIGH);
  digitalWrite(F_MC2, LOW);
  analogWrite(FORWARD_VENT, speed);
}
void startReverse(int speed) {  //Скорость вращения вентиляторов реверсивного направления
  digitalWrite(REVERSE_VENT, LOW);
  digitalWrite(R_MC1, HIGH);
  digitalWrite(R_MC2, LOW);
  analogWrite(REVERSE_VENT, speed);
}

void change_parameters() {  //Ручная, автоматическая настройка параметров
  auto_Mode = control_settings[0];
  if (auto_Mode == 1) {
    tempSetpoint = control_settings[1];
    humidSetpoint = control_settings[2];
  } else {
    tempSetpoint = temperatures[stage_index];
    humidSetpoint = humids[stage_index];
  }
}

void remaining_time() { //Отчёт окончания времени сушки
  if (millis() - time_leftTimr >= 1000) {
    time_leftTimr = millis();
    if (total_time > 0) {
      total_time--;
    } else {
      canDry = 0; //Остановка сушки
    }
    double packet[1];
    packet[0] = total_time;
    sendPacket(1, packet, 1);
  }
}

void sendPacket(int key, double* data, int amount) { //Отправки пакета на ПК: ключ, данные, длина пакета
  Serial.print(key);
  Serial.print(",");
  for (int i = 0; i < amount; i++) {
    Serial.print(data[i]);
    if (i != amount - 1) {
      Serial.print(",");  //Разделитель данных
    }
  }
  Serial.print("\n"); //Терминатор - конец данных
}