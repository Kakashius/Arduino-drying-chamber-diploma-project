class Tree:
    treeList = {    # Список пород древесины и доступных режимов сушки
        "Берёза": ["Нормальный", "Форсированный"],
        "Сосна": ["Мягкий", "Нормальный", "Форсированный"]
    }

    def __init__(self, tree, mode, size, width, startHum, setHum):
        self.tree = str(tree)    # Порода
        self.mode = str(mode)    # Режим
        self.size = float(size)    # Толщина
        self.width = float(width)  # Ширина
        self.startHum = int(startHum)   # Начальная влажность
        self.setHum = int(setHum) # Конечная влажность

        self.define_step_params(self.tree)  # Задать параметры ступеней сушки
        self.steps = {1: [self.t_I, self.dt_I, self.w_I],
                      2: [self.t_II, self.dt_II, self.w_II],
                      3: [self.t_III, self.dt_III, self.w_III]}  # Параметры ступеней сушки
        self.category = self.define_category()  #Задать категорию сушки
        self.stages = self.define_stages()  # Задать этапы сушки
        self.ventSpeed = self.define_vent_speed()   #Задать скорость вентиляторов

        self.totalTime = self.define_total_time()  # Определить приблизительную общую продолжительность сушки
        self.tree_resist = self.define_tree_resist(self.size, self.width)    # Определить сопротивлеение сухой древесины
        
        self.stepTime = self.define_step_time() #Уставновить время для 1, 2, 3 этапов
        self.end_proc_time = self.define_end_proc_time()    # Определить время конечной влаготеплообработки
        self.mid_proc_time = self.define_mid_proc_time()    # Определить время промежуточной влаготеплообработки

        self.show_to_window = self.show_params_for_window() # Показать в диалоговом окне

        self.const_params = self.define_const_params()  # Отправка неизменяемых параметров

        self.constant_file_parameters = [str(self.startHum),    #Хранение текстовых параметров в файле
                                        str(self.setHum),
                                        self.category,
                                        self.tree,
                                        str(self.size) + " x " + str(self.width),
                                        self.mode]
        self.stages_file = list(self.stages.values())   # Список этапов текущей сушки

        '''{1: "Прогрев камеры",
        2: "Прогрев древесины",
        3: "Сушка (1 этап)",
        4: "Сушка (2 этап)",
        5: "Сушка (3 этап)",
        6: "Кондиционирование",
        7: "Охлаждение"}'''
        '''
        {1: "Прогрев камеры",
        2: "Прогрев древесины",
        3: "Сушка (1 этап)",
        4: "Сушка (2 этап)",
        5: "Сушка (3 этап)",
        6: "Конеч. влаготеплообработка",
        7: "Кондиционирование",
        8: "Охлаждение"}
        '''
        '''
        {1: "Прогрев камеры",
        2: "Прогрев древесины",
        3: "Сушка (1 этап)",
        4: "Сушка (2 этап)",
        5: "Промеж. влаготеплообработка",
        6: "Сушка (3 этап)",
        7: "Конеч. влаготеплообработка",
        8: "Кондиционирование",
        9: "Охлаждение"}
        '''

    def define_number_of_steps(self):   # Параметры ступеней и влаготеплообработки
        if self.startHum > 30:
            if len(self.stages) == 7:
                return [self.start_step1(),  # Параметры 1 ступени сушки
                        self.start_step2(),  # Параметры 2 ступени сушки
                        self.start_step3()  # Параметры 3 ступени сушки
                        ]
            elif len(self.stages) == 8:
                return [self.start_step1(),  # Параметры 1 ступени сушки
                        self.start_step2(),  # Параметры 2 ступени сушки
                        self.start_step3(),  # Параметры 3 ступени сушки
                        self.start_end_proc()  # Параметры конечной влаготеплообработки
                        ]
            else:
                return [self.start_step1(),  # Параметры 1 ступени сушки
                        self.start_step2(),  # Параметры 2 ступени сушки
                        self.start_mid_proc(),  # Параметры промежуточной влаготеплообработки
                        self.start_step3(),  # Параметры 3 ступени сушки
                        self.start_end_proc()  # Параметры конечной влаготеплообработки
                        ]
        elif 20 < self.startHum <= 30:
            if len(self.stages) == 7:
                return [self.start_step2(),  # Параметры 2 ступени сушки
                        self.start_step3()  # Параметры 3 ступени сушки
                        ]
            elif len(self.stages) == 8:
                return [self.start_step2(),  # Параметры 2 ступени сушки
                        self.start_step3(),  # Параметры 3 ступени сушки
                        self.start_end_proc()  # Параметры конечной влаготеплообработки
                        ]
            else:
                return [self.start_step2(),  # Параметры 2 ступени сушки
                        self.start_mid_proc(),  # Параметры промежуточной влаготеплообработки
                        self.start_step3(),  # Параметры 3 ступени сушки
                        self.start_end_proc()  # Параметры конечной влаготеплообработки
                        ]
        else:
            if len(self.stages) == 7:
                return [self.start_step3()  # Параметры 3 ступени сушки
                        ]
            elif len(self.stages) == 8:
                return [self.start_step3(),  # Параметры 3 ступени сушки
                        self.start_end_proc()  # Параметры конечной влаготеплообработки
                        ]
            else:
                return [self.start_step3(),  # Параметры 3 ступени сушки
                        self.start_end_proc()  # Параметры конечной влаготеплообработки
                        ]   #
    def execute_proccess(self, define_conditionate_hum):    # Определить параметры в Arduino
        self.conditionate_hum = int(define_conditionate_hum)    #Вводим значение с диалогового окна
        done = [
                self.const_params,
                self.start_heat(),  # Параметры прогрева камеры
                self.start_dry(),  # Параметры прогрева древесины
                *self.define_number_of_steps(),   # Параметры ступеней и влаготеплообработки
                self.start_conditionate(self.conditionate_hum),  # Параметры кондиционирования древесины, ввод по всплывающему окну
                self.start_cooling()  # Параметры охлаждения камеры
                ]
        return done
    
    def show_params_for_window(self):   # Показать параметры в диалоговом окне
        if "Конеч. влаготеплообработка" in self.stages.values():
            show_temp = self.steps[3][0] + 8 if (self.steps[3][0] + 8) <= 100 else 100
        else:
            show_temp = self.steps[3][0] if self.steps[3][0] <= 100 else 100
        return str(show_temp), str(self.setHum + 1)

    def define_const_params(self):
        return ["1"] + [
                        str(self.tree_resist),
                        str(self.totalTime)
                        ]

    @classmethod
    def stop(cls): #При нажатии СТОП, отправка на отключение сушки !!!!!!!
        return ["0"]
    def start_heat(self):
        temp_set = 60
        humid_set = 20
        time_hrs = 3
        vent_speed = self.ventSpeed[1]
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 0
        valve_pwr = 0
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    def start_dry(self):
        temp_set = self.steps[1][0]
        humid_set = self.steps[1][2]
        time_hrs = 0
        vent_speed = self.ventSpeed[2]
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 1
        valve_pwr = 1
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    def start_step1(self):
        temp_set = self.steps[1][0]
        humid_set = self.steps[1][2]
        time_hrs = self.stepTime
        vent_speed = self.ventSpeed[3]
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 1
        valve_pwr = 1
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    def start_step2(self):
        temp_set = self.steps[2][0]
        humid_set = self.steps[2][2]
        time_hrs = self.stepTime
        vent_speed = self.ventSpeed[4]
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 1
        valve_pwr = 1
        return ["3"] +list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    def start_step3(self):
        temp_set = self.steps[3][0]
        humid_set = self.steps[3][2]
        time_hrs = self.stepTime
        vent_speed = self.ventSpeed[5]
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 1
        valve_pwr = 1
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    def start_conditionate(self, conditionate_hum):
        if "Конеч. влаготеплообработка" in self.stages.values():
            temp_set = self.steps[3][0] + 8 + 5 if (self.steps[3][0] + 8 + 5) <= 100 else 100
            humid_set = conditionate_hum    
            time_hrs = self.end_proc_time
            vent_speed = self.ventSpeed[7]
            heat_pwr = 1
            vent_pwr = 1
            windows_pwr = 1
            valve_pwr = 1
        else:
            temp_set = self.steps[3][0] + 5 if (self.steps[3][0] + 5) <= 100 else 100
            humid_set = conditionate_hum    
            time_hrs = self.end_proc_time
            vent_speed = self.ventSpeed[6]
            heat_pwr = 1
            vent_pwr = 1
            windows_pwr = 1
            valve_pwr = 1
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    
    def start_cooling(self):
        temp_set = 40
        humid_set = 0   
        time_hrs = 0
        vent_speed = 0
        heat_pwr = 0
        vent_pwr = 0
        windows_pwr = 1
        valve_pwr = 0
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))

    def start_mid_proc(self):
        temp_set = (self.steps[2][0] + 8) if (self.steps[2][0] + 8) <= 100 else 100
        humid_set = 95
        time_hrs = self.mid_proc_time
        vent_speed = self.ventSpeed[5]
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 1
        valve_pwr = 1
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))
    
    def start_end_proc(self):
        temp_set = (self.steps[3][0] + 8) if (self.steps[3][0] + 8) <= 100 else 100
        humid_set = 95
        time_hrs = self.end_proc_time
        vent_speed = 3 if self.size <= 50 else 2
        heat_pwr = 1
        vent_pwr = 1
        windows_pwr = 1
        valve_pwr = 1
        return ["3"] + list(map(str, (temp_set, humid_set, vent_speed, time_hrs, heat_pwr, vent_pwr, windows_pwr, valve_pwr)))

    def define_step_params(self, tree_type):
            if tree_type in ["Сосна", "Ель", "Пихта", "Кедр"]:
                if self.mode == "Мягкий":
                    if self.size < 22:
                        self.t_I = 57
                        self.dt_I = 6
                        self.w_I = 72
                        self.t_II = 64
                        self.dt_II =10
                        self.w_II =59
                        self.t_III = 77
                        self.dt_III =26
                        self.w_III =27
                    elif 22 <= self.size < 30:
                        self.t_I = 57
                        self.dt_I = 5
                        self.w_I =76
                        self.t_II = 61
                        self.dt_II =9
                        self.w_II =62
                        self.t_III = 77
                        self.dt_III =25
                        self.w_III =29
                    elif 30 <= self.size < 40:
                        self.t_I = 52
                        self.dt_I =5
                        self.w_I =75
                        self.t_II =55
                        self.dt_II =8
                        self.w_II =64
                        self.t_III =70
                        self.dt_III =23
                        self.w_III =29
                    elif 40 <= self.size < 50:
                        self.t_I = 52
                        self.dt_I = 4
                        self.w_I = 80
                        self.t_II =55
                        self.dt_II = 7
                        self.w_II = 68
                        self.t_III =70
                        self.dt_III =22
                        self.w_III =31
                    elif 50 <= self.size < 60:
                        self.t_I = 52
                        self.dt_I = 4
                        self.w_I =80
                        self.t_II =55
                        self.dt_II =7
                        self.w_II =68
                        self.t_III =70
                        self.dt_III =22
                        self.w_III =31
                    elif 60 <= self.size < 70:
                        self.t_I = 52
                        self.dt_I =3
                        self.w_I =84
                        self.t_II =55
                        self.dt_II =5
                        self.w_II =76
                        self.t_III =70
                        self.dt_III =21
                        self.w_III =33
                    elif 70 <= self.size < 85:
                        self.t_I = 52
                        self.dt_I =3
                        self.w_I =84
                        self.t_II =55
                        self.dt_II =5
                        self.w_II =76
                        self.t_III =70
                        self.dt_III =21
                        self.w_III =33
                    else:
                        self.t_I = 47
                        self.dt_I = 2
                        self.w_I = 90
                        self.t_II =50
                        self.dt_II =5
                        self.w_II =75
                        self.t_III =62
                        self.dt_III =18
                        self.w_III =36
                elif self.mode == "Нормальный":
                    if self.size < 22:
                        self.t_I = 82
                        self.dt_I =10
                        self.w_I =65
                        self.t_II =87
                        self.dt_II =14
                        self.w_II =55
                        self.t_III =108
                        self.dt_III =35
                        self.w_III =24
                    elif 22 <= self.size < 30:
                        self.t_I = 75
                        self.dt_I =7
                        self.w_I =73
                        self.t_II =80
                        self.dt_II =11
                        self.w_II =61
                        self.t_III =100
                        self.dt_III =31
                        self.w_III =27
                    elif 30 <= self.size < 40:
                        self.t_I = 75
                        self.dt_I =5
                        self.w_I =80
                        self.t_II =80
                        self.dt_II =9
                        self.w_II =66
                        self.t_III =100
                        self.dt_III =29
                        self.w_III =30
                    elif 40 <= self.size < 50:
                        self.t_I = 69
                        self.dt_I =5
                        self.w_I =79
                        self.t_II =73
                        self.dt_II =8
                        self.w_II =69
                        self.t_III =91
                        self.dt_III =26
                        self.w_III =33
                    elif 50 <= self.size < 60:
                        self.t_I = 69
                        self.dt_I =4
                        self.w_I =83
                        self.t_II =73
                        self.dt_II =7
                        self.w_II =72
                        self.t_III =91
                        self.dt_III =25
                        self.w_III =34
                    elif 60 <= self.size < 70:
                        self.t_I = 63
                        self.dt_I =3
                        self.w_I =86
                        self.t_II =67
                        self.dt_II =6
                        self.w_II =75
                        self.t_III =83
                        self.dt_III =23
                        self.w_III =34
                    elif 70 <= self.size < 85:
                        self.t_I =57
                        self.dt_I =3
                        self.w_I =85
                        self.t_II =61
                        self.dt_II =6
                        self.w_II =74
                        self.t_III =77
                        self.dt_III =22
                        self.w_III =34
                    else:
                        self.t_I = 52
                        self.dt_I =3
                        self.w_I =84
                        self.t_II =55
                        self.dt_II =5
                        self.w_II =76
                        self.t_III =70
                        self.dt_III =21
                        self.w_III =33
                else:
                    if self.size < 22:
                        self.t_I =90
                        self.dt_I =11
                        self.w_I =63
                        self.t_II =95
                        self.dt_II =15
                        self.w_II =54
                        self.t_III =120
                        self.dt_III =38
                        self.w_III =34
                    elif 22 <= self.size < 30:
                        self.t_I = 90
                        self.dt_I =9
                        self.w_I =69
                        self.t_II =95
                        self.dt_II =13
                        self.w_II =60
                        self.t_III =120
                        self.dt_III =37
                        self.w_III =25
                    elif 30 <= self.size < 40:
                        self.t_I =90
                        self.dt_I =7
                        self.w_I =75
                        self.t_II =95
                        self.dt_II =11
                        self.w_II =65
                        self.t_III =120
                        self.dt_III =36
                        self.w_III =26
                    elif 40 <= self.size < 50:
                        self.t_I = 82
                        self.dt_I =6
                        self.w_I =77
                        self.t_II =87
                        self.dt_II =10
                        self.w_II =66
                        self.t_III =108
                        self.dt_III =31
                        self.w_III =30
                    elif 50 <= self.size < 60:
                        self.t_I =82
                        self.dt_I =4
                        self.w_I =84
                        self.t_II =87
                        self.dt_II =8
                        self.w_II =72
                        self.t_III =108
                        self.dt_III =29
                        self.w_III =32
                    elif 60 <= self.size < 70:
                        self.t_I = 75
                        self.dt_I =4
                        self.w_I =84
                        self.t_II =80
                        self.dt_II =8
                        self.w_II =70
                        self.t_III =100
                        self.dt_III =28
                        self.w_III =32
                    elif 70 <= self.size < 85:
                        self.t_I = 75
                        self.dt_I =4
                        self.w_I =84
                        self.t_II =80
                        self.dt_II =8
                        self.w_II =70
                        self.t_III =100
                        self.dt_III =28
                        self.w_III =32
                    else:
                        self.t_I = 75
                        self.dt_I =4
                        self.w_I =84
                        self.t_II =80
                        self.dt_II =8
                        self.w_II =70
                        self.t_III =100
                        self.dt_III =28
                        self.w_III =32

            elif tree_type in ["Берёза", "Ольха"]:
                if self.mode == "Нормальный":
                    if self.size < 22:
                        self.t_I =75
                        self.dt_I =9
                        self.w_I =66
                        self.t_II =80
                        self.dt_II =13
                        self.w_II =55
                        self.t_III =100
                        self.dt_III =33
                        self.w_III =25

                    elif 22 <= self.size < 30:
                        self.t_I =69
                        self.dt_I =6
                        self.w_I =76
                        self.t_II =73
                        self.dt_II =10
                        self.w_II =63
                        self.t_III =91
                        self.dt_III =28
                        self.w_III =30

                    elif 30 <= self.size < 40:
                        self.t_I = 69
                        self.dt_I =5
                        self.w_I =79
                        self.t_II =73
                        self.dt_II =8
                        self.w_II =69
                        self.t_III =91
                        self.dt_III =26
                        self.w_III =33
                    elif 40 <= self.size < 50:
                        self.t_I = 63
                        self.dt_I =4
                        self.w_I =82
                        self.t_II =67
                        self.dt_II =7
                        self.w_II =71
                        self.t_III =83
                        self.dt_III =24
                        self.w_III =32
                    elif 50 <= self.size < 60:
                        self.t_I = 57
                        self.dt_I =3
                        self.w_I =85
                        self.t_II =61
                        self.dt_II =6
                        self.w_II =74
                        self.t_III =77
                        self.dt_III =22
                        self.w_III =34
                    elif 60 <= self.size < 70:
                        self.t_I = 52
                        self.dt_I =3
                        self.w_I =84
                        self.t_II =55
                        self.dt_II =5
                        self.w_II =76
                        self.t_III =70
                        self.dt_III =21
                        self.w_III =33
                    elif 70 <= self.size < 85:
                        self.t_I = 47
                        self.dt_I =2
                        self.w_I =90
                        self.t_II =50
                        self.dt_II =5
                        self.w_II =75
                        self.t_III =62
                        self.dt_III =18
                        self.w_III =36
                    else:
                        self.t_I = 42
                        self.dt_I =2
                        self.w_I =89
                        self.t_II =45
                        self.dt_II =4
                        self.w_II =79
                        self.t_III =57
                        self.dt_III =17
                        self.w_III =36
                elif self.mode == "Форсированный":
                    if self.size < 22:
                        self.t_I = 82
                        self.dt_I =10
                        self.w_I =65
                        self.t_II =87
                        self.dt_II =14
                        self.w_II =55
                        self.t_III =108
                        self.dt_III =35
                        self.w_III =24
                    elif 22 <= self.size < 30:
                        self.t_I = 75
                        self.dt_I =7
                        self.w_I =73
                        self.t_II =80
                        self.dt_II =11
                        self.w_II =61
                        self.t_III =100
                        self.dt_III =31
                        self.w_III =27
                    elif 30 <= self.size < 40:
                        self.t_I = 75
                        self.dt_I =5
                        self.w_I =80
                        self.t_II =80
                        self.dt_II =9
                        self.w_II =66
                        self.t_III =100
                        self.dt_III =29
                        self.w_III =30

                    elif 40 <= self.size < 50:
                        self.t_I = 69
                        self.dt_I =5
                        self.w_I =79
                        self.t_II =73
                        self.dt_II =8
                        self.w_II =69
                        self.t_III =91
                        self.dt_III =26
                        self.w_III =33

                    elif 50 <= self.size < 60:
                        self.t_I = 69
                        self.dt_I = 5
                        self.w_I = 79
                        self.t_II = 73
                        self.dt_II = 8
                        self.w_II = 69
                        self.t_III = 91
                        self.dt_III = 26
                        self.w_III = 33

                    elif 60 <= self.size < 70:
                        self.t_I = 69
                        self.dt_I = 5
                        self.w_I = 79
                        self.t_II = 73
                        self.dt_II = 8
                        self.w_II = 69
                        self.t_III = 91
                        self.dt_III = 26
                        self.w_III = 33

                    elif 70 <= self.size < 85:
                        self.t_I = 69
                        self.dt_I = 5
                        self.w_I = 79
                        self.t_II = 73
                        self.dt_II = 8
                        self.w_II = 69
                        self.t_III = 91
                        self.dt_III = 26
                        self.w_III = 33

                    else:
                        self.t_I = 69
                        self.dt_I = 5
                        self.w_I = 79
                        self.t_II = 73
                        self.dt_II = 8
                        self.w_II = 69
                        self.t_III = 91
                        self.dt_III = 26
                        self.w_III = 33
    def define_vent_speed(self):
        if self.tree in self.treeList.keys():
            if self.size <= 50: # Скорости вентиляторов в зависимости от этапа до 55 мм
                if "Промеж. влаготеплообработка" in self.stages.values() and  "Конеч. влаготеплообработка" in self.stages.values():
                    return {1: 3,
                            2: 3,
                            3: 4,
                            4: 3,
                            5: 3,
                            6: 3,
                            7: 3,
                            8: 3,
                            9: 0}
                elif not "Промеж. влаготеплообработка" in self.stages.values() and "Конеч. влаготеплообработка" in self.stages.values():
                    return {1: 3,
                            2: 3,
                            3: 4,
                            4: 3,
                            5: 3,
                            6: 3,
                            7: 3,
                            8: 0,}
                else:
                    return {1: 3,
                            2: 3,
                            3: 4,
                            4: 3,
                            5: 3,
                            6: 3,
                            7: 0,}
            else:
                if "Промеж. влаготеплообработка" in self.stages.values() and  "Конеч. влаготеплообработка" in self.stages.values():
                    return {1: 2,
                            2: 2,
                            3: 3,
                            4: 2,
                            5: 2,
                            6: 2,
                            7: 2,
                            8: 2,
                            9: 0}
                elif not "Промеж. влаготеплообработка" in self.stages.values() and "Конеч. влаготеплообработка" in self.stages.values():
                    return {1: 2,
                            2: 2,
                            3: 3,
                            4: 2,
                            5: 2,
                            6: 2,
                            7: 2,
                            8: 0,}
                else:
                    return {1: 2,
                            2: 2,
                            3: 3,
                            4: 2,
                            5: 2,
                            6: 2,
                            7: 0,}
                       
    def define_step_time(self):
        if self.tree == "Берёза":
            return round(2.5 * (self.size / 10))
        elif self.tree == "Сосна":
            return 2 * (round(self.size / 10))

    def define_end_proc_time(self):
        if self.tree == "Берёза":
            if self.size < 30:
                return 3
            elif 30 <= self.size < 40:
                return 6
            elif 40 <= self.size < 50:
                return 12
            elif 50 <= self.size < 60:
                return 18
            elif 60 <= self.size < 80:
                return 30
            else:
                return 60
        elif self.tree == "Сосна":
            if self.size < 30:
                return 2
            elif 30 <= self.size < 40:
                return 3
            elif 40 <= self.size < 50:
                return 6
            elif 50 <= self.size < 60:
                return 9
            elif 60 <= self.size < 80:
                return 14
            else:
                return 24
    
    def define_mid_proc_time(self):
        if self.tree == "Сосна":
            if 60 <= self.size < 80:
                return 7
            elif 80 <= self.size:
                return 12
            else:
                return 0
        if self.tree == "Берёза":
            if 50 <= self.size < 60:
                return 9
            elif 60 <= self.size < 80:
                return 15
            elif 80 <= self.size:
                return 30
            else:
                return 0
       
    def define_category(self):
        if self.size <= 38:
            if self.setHum <= 8:
                return "I"
            elif 8 < self.setHum <= 10:
                return "II"
            elif 10 < self.setHum <= 15:
                return "III"
            else:
                return "0"
        elif 38 < self.size <= 50:
            if self.setHum <= 8:
                return "I"
            elif 8 < self.setHum <= 10:
                return "II"
            elif 10 < self.setHum <= 15:
                return "III"
            else:
                return "0"
        else:
            if self.setHum <= 8:
                return "I"
            elif 8 < self.setHum <= 10:
                return "II"
            elif 10 < self.setHum <= 15:
                return "III"
            else:
                return "0"
    def define_stages(self):
        if self.category in ("I", "II"):
            if self.tree in ("Сосна", "Ель", "Пихта", "Осина", "Тополь", "Кедр", "Липа"):
                if self.size < 60:
                    return {1: "Прогрев камеры",
                       2: "Прогрев древесины",
                       3: "Сушка (1 этап)",
                       4: "Сушка (2 этап)",
                       5: "Сушка (3 этап)",
                       6: "Конеч. влаготеплообработка",
                       7: "Кондиционирование",
                       8: "Охлаждение"}
                else:
                    return {1: "Прогрев камеры",
                       2: "Прогрев древесины",
                       3: "Сушка (1 этап)",
                       4: "Сушка (2 этап)",
                       5: "Промеж. влаготеплообработка",
                       6: "Сушка (3 этап)",
                       7: "Конеч. влаготеплообработка",
                       8: "Кондиционирование",
                       9: "Охлаждение"}
            elif self.tree in ("Берёза", "Ольха"):
                if self.size < 50:
                    return {1: "Прогрев камеры",
                       2: "Прогрев древесины",
                       3: "Сушка (1 этап)",
                       4: "Сушка (2 этап)",
                       5: "Сушка (3 этап)",
                       6: "Конеч. влаготеплообработка",
                       7: "Кондиционирование",
                       8: "Охлаждение"}
                else:
                    return {1: "Прогрев камеры",
                       2: "Прогрев древесины",
                       3: "Сушка (1 этап)",
                       4: "Сушка (2 этап)",
                       5: "Промеж. влаготеплообработка",
                       6: "Сушка (3 этап)",
                       7: "Конеч. влаготеплообработка",
                       8: "Кондиционирование",
                       9: "Охлаждение"}
        else:
            return {1: "Прогрев камеры",
                       2: "Прогрев древесины",
                       3: "Сушка (1 этап)",
                       4: "Сушка (2 этап)",
                       5: "Сушка (3 этап)",
                       6: "Кондиционирование",
                       7: "Охлаждение"}
    
    def define_total_time(self):
        initial_time = self.define_initial_time(self.size, self.width)
        mode_time = self.define_mode_time(self.mode)
        vent_speed_time = self.define_vent_speed_time(initial_time * mode_time)
        category_time = self.define_category_time(self.category)
        hum_time = self.define_hum_time(self.startHum, self.setHum)
        return int((initial_time * mode_time * vent_speed_time * category_time * hum_time) * 3600)
        
    def define_initial_time(self, size, width):
        if self.tree == "Сосна":
            if width < 100:
                if size < 16:
                    return 25
                elif 16 <= size < 19:
                    return 31
                elif 19 <= size < 22:
                    return 37
                elif 22 <= size < 25:
                    return 48
                elif 25 <= size < 32:
                    return 70
                elif 32 <= size < 40:
                    return 85
                elif 40 <= size < 50:
                    return 100
                elif 50 <= size < 60:
                    return 120
                elif 60 <= size < 70:
                    return 140
                elif 70 <= size < 75:
                    return 155
                else:
                    return 230
            elif 100 <= width < 140:
                if size < 16:
                    return 27
                elif 16 <= size < 19:
                    return 33
                elif 19 <= size < 22:
                    return 40
                elif 22 <= size < 25:
                    return 51
                elif 25 <= size < 32:
                    return 75
                elif 32 <= size < 40:
                    return 90
                elif 40 <= size < 50:
                    return 105
                elif 50 <= size < 60:
                    return 130
                elif 60 <= size < 70:
                    return 155
                elif 70 <= size < 75:
                    return 180
                else:
                    return 280
            elif 140 <= width < 180:
                if size < 16:
                    return 29
                elif 16 <= size < 19:
                    return 35
                elif 19 <= size < 22:
                    return 43
                elif 22 <= size < 25:
                    return 54
                elif 25 <= size < 32:
                    return 80
                elif 32 <= size < 40:
                    return 95
                elif 40 <= size < 50:
                    return 110
                elif 50 <= size < 60:
                    return 140
                elif 60 <= size < 70:
                    return 175
                elif 70 <= size < 75:
                    return 210
                else:
                    return 350
            else:
                if size < 16:
                    return 31
                elif 16 <= size < 19:
                    return 37
                elif 19 <= size < 22:
                    return 46
                elif 22 <= size < 25:
                    return 57
                elif 25 <= size < 32:
                    return 85
                elif 32 <= size < 40:
                    return 100
                elif 40 <= size < 50:
                    return 120
                elif 50 <= size < 60:
                    return 160
                elif 60 <= size < 70:
                    return 210
                elif 70 <= size < 75:
                    return 260
                else:
                    return 465
        else:
            if width < 100:
                if size < 16:
                    return 35
                elif 16 <= size < 19:
                    return 44
                elif 19 <= size < 22:
                    return 50
                elif 22 <= size < 25:
                    return 66
                elif 25 <= size < 32:
                    return 90
                elif 32 <= size < 40:
                    return 100
                elif 40 <= size < 50:
                    return 125
                elif 50 <= size < 60:
                    return 170
                elif 60 <= size < 70:
                    return 220
                elif 70 <= size < 75:
                    return 220
                else:
                    return 220
            elif 100 <= width < 140:
                if size < 16:
                    return 38
                elif 16 <= size < 19:
                    return 47
                elif 19 <= size < 22:
                    return 53
                elif 22 <= size < 25:
                    return 70
                elif 25 <= size < 32:
                    return 95
                elif 32 <= size < 40:
                    return 105
                elif 40 <= size < 50:
                    return 135
                elif 50 <= size < 60:
                    return 190
                elif 60 <= size < 70:
                    return 270
                elif 70 <= size < 75:
                    return 270
                else:
                    return 270
            elif 140 <= width < 180:
                if size < 16:
                    return 41
                elif 16 <= size < 19:
                    return 50
                elif 19 <= size < 22:
                    return 56
                elif 22 <= size < 25:
                    return 74
                elif 25 <= size < 32:
                    return 100
                elif 32 <= size < 40:
                    return 110
                elif 40 <= size < 50:
                    return 150
                elif 50 <= size < 60:
                    return 220
                elif 60 <= size < 70:
                    return 330
                elif 70 <= size < 75:
                    return 330
                else:
                    return 330
            else:
                if size < 16:
                    return 44
                elif 16 <= size < 19:
                    return 53
                elif 19 <= size < 22:
                    return 59
                elif 22 <= size < 25:
                    return 80
                elif 25 <= size < 32:
                    return 105
                elif 32 <= size < 40:
                    return 115
                elif 40 <= size < 50:
                    return 170
                elif 50 <= size < 60:
                    return 260
                elif 60 <= size < 70:
                    return 400
                elif 70 <= size < 75:
                    return 400
                else:
                    return 400
    def define_mode_time(self, mode):
        if mode == "Форсированный":
            return 0.8
        elif mode == "Нормальный":
            return 1
        else:
            return 1.7

    def define_vent_speed_time(self, res):
        if res < 20:
            return 0.65
        elif 20 <= res < 40:
            return 0.7
        elif 40 <= res < 60:
            return 0.75
        elif 60 <= res < 80:
            return 0.8
        elif 80 <= res < 100:
            return 0.85
        elif 100 <= res < 140:
            return 0.9
        elif 140 <= res < 180:
            return 0.93
        elif 180 <= res < 200:
            return 0.95
        else:
            return 1

    def define_category_time(self, category):
        if category == "I":
            return 1.25
        elif category == "II":
            return 1.15
        elif category == "III":
            return 1.05
        else:
            return 1

    def define_hum_time(self, start, end):
        if end <= 6:
            if start < 14:
                return 0.52
            elif 14 <= start < 16:
                return 0.61
            elif 16 <= start < 18:
                return 0.68
            elif 18 <= start < 20:
                return 0.75
            elif 20 <= start < 22:
                return 0.81
            elif 22 <= start < 24:
                return 0.86
            elif 24 <= start < 26:
                return 0.91
            elif 26 <= start < 28:
                return 0.96
            elif 28 <= start < 30:
                return 1
            elif 30 <= start < 35:
                return 1.1
            elif 35 <= start < 40:
                return 1.18
            elif 40 <= start < 45:
                return 1.25
            elif 45 <= start < 50:
                return 1.32
            elif 50 <= start < 55:
                return 1.38
            elif 55 <= start < 60:
                return 1.43
            elif 60 <= start < 65:
                return 1.48
            elif 65 <= start < 70:
                return 1.52
            elif 70 <= start < 80:
                return 1.61
            elif 80 <= start < 90:
                return 1.68
            elif 90 <= start < 100:
                return 1.75
            elif 100 <= start < 110:
                return 1.81
            else:
                return 1.86
        elif 6 < end <= 7:
            if start < 14:
                return 0.43
            elif 14 <= start < 16:
                return 0.52
            elif 16 <= start < 18:
                return 0.59
            elif 18 <= start < 20:
                return 0.65
            elif 20 <= start < 22:
                return 0.71
            elif 22 <= start < 24:
                return 0.77
            elif 24 <= start < 26:
                return 0.82
            elif 26 <= start < 28:
                return 0.86
            elif 28 <= start < 30:
                return 0.9
            elif 30 <= start < 35:
                return 1
            elif 35 <= start < 40:
                return 1.08
            elif 40 <= start < 45:
                return 1.15
            elif 45 <= start < 50:
                return 1.22
            elif 50 <= start < 55:
                return 1.28
            elif 55 <= start < 60:
                return 1.33
            elif 60 <= start < 65:
                return 1.38
            elif 65 <= start < 70:
                return 1.43
            elif 70 <= start < 80:
                return 1.51
            elif 80 <= start < 90:
                return 1.58
            elif 90 <= start < 100:
                return 1.65
            elif 100 <= start < 110:
                return 1.71
            else:
                return 1.76
        elif 7 < end <= 8:
            if start < 14:
                return 0.35
            elif 14 <= start < 16:
                return 0.43
            elif 16 <= start < 18:
                return 0.5
            elif 18 <= start < 20:
                return 0.57
            elif 20 <= start < 22:
                return 0.63
            elif 22 <= start < 24:
                return 0.68
            elif 24 <= start < 26:
                return 0.73
            elif 26 <= start < 28:
                return 0.78
            elif 28 <= start < 30:
                return 0.82
            elif 30 <= start < 35:
                return 0.92
            elif 35 <= start < 40:
                return 1
            elif 40 <= start < 45:
                return 1.07
            elif 45 <= start < 50:
                return 1.14
            elif 50 <= start < 55:
                return 1.2
            elif 55 <= start < 60:
                return 1.25
            elif 60 <= start < 65:
                return 1.30
            elif 65 <= start < 70:
                return 1.35
            elif 70 <= start < 80:
                return 1.43
            elif 80 <= start < 90:
                return 1.51
            elif 90 <= start < 100:
                return 1.57
            elif 100 <= start < 110:
                return 1.62
            else:
                return 1.68
        elif 8 < end <= 9:
            if start < 14:
                return 0.28
            elif 14 <= start < 16:
                return 0.36
            elif 16 <= start < 18:
                return 0.43
            elif 18 <= start < 20:
                return 0.5
            elif 20 <= start < 22:
                return 0.56
            elif 22 <= start < 24:
                return 0.61
            elif 24 <= start < 26:
                return 0.66
            elif 26 <= start < 28:
                return 0.71
            elif 28 <= start < 30:
                return 0.75
            elif 30 <= start < 35:
                return 0.84
            elif 35 <= start < 40:
                return 0.93
            elif 40 <= start < 45:
                return 1
            elif 45 <= start < 50:
                return 1.06
            elif 50 <= start < 55:
                return 1.12
            elif 55 <= start < 60:
                return 1.18
            elif 60 <= start < 65:
                return 1.23
            elif 65 <= start < 70:
                return 1.27
            elif 70 <= start < 80:
                return 1.35
            elif 80 <= start < 90:
                return 1.43
            elif 90 <= start < 100:
                return 1.5
            elif 100 <= start < 110:
                return 1.55
            else:
                return 1.61
        elif 9 < end <= 10:
            if start < 14:
                return 0.21
            elif 14 <= start < 16:
                return 0.3
            elif 16 <= start < 18:
                return 0.37
            elif 18 <= start < 20:
                return 0.43
            elif 20 <= start < 22:
                return 0.49
            elif 22 <= start < 24:
                return 0.54
            elif 24 <= start < 26:
                return 0.59
            elif 26 <= start < 28:
                return 0.64
            elif 28 <= start < 30:
                return 0.68
            elif 30 <= start < 35:
                return 0.78
            elif 35 <= start < 40:
                return 0.86
            elif 40 <= start < 45:
                return 0.93
            elif 45 <= start < 50:
                return 1
            elif 50 <= start < 55:
                return 1.06
            elif 55 <= start < 60:
                return 1.11
            elif 60 <= start < 65:
                return 1.16
            elif 65 <= start < 70:
                return 1.21
            elif 70 <= start < 80:
                return 1.29
            elif 80 <= start < 90:
                return 1.36
            elif 90 <= start < 100:
                return 1.43
            elif 100 <= start < 110:
                return 1.49
            else:
                return 1.55
        elif 10 < end <= 11:
            if start < 14:
                return 0.15
            elif 14 <= start < 16:
                return 0.23
            elif 16 <= start < 18:
                return 0.30
            elif 18 <= start < 20:
                return 0.37
            elif 20 <= start < 22:
                return 0.43
            elif 22 <= start < 24:
                return 0.49
            elif 24 <= start < 26:
                return 0.54
            elif 26 <= start < 28:
                return 0.58
            elif 28 <= start < 30:
                return 0.62
            elif 30 <= start < 35:
                return 0.72
            elif 35 <= start < 40:
                return 0.80
            elif 40 <= start < 45:
                return 0.87
            elif 45 <= start < 50:
                return 0.94
            elif 50 <= start < 55:
                return 1
            elif 55 <= start < 60:
                return 1.05
            elif 60 <= start < 65:
                return 1.1
            elif 65 <= start < 70:
                return 1.15
            elif 70 <= start < 80:
                return 1.23
            elif 80 <= start < 90:
                return 1.3
            elif 90 <= start < 100:
                return 1.37
            elif 100 <= start < 110:
                return 1.43
            else:
                return 1.49
        elif 11 < end <= 12:
            if start < 14:
                return 0.1
            elif 14 <= start < 16:
                return 0.18
            elif 16 <= start < 18:
                return 0.25
            elif 18 <= start < 20:
                return 0.32
            elif 20 <= start < 22:
                return 0.38
            elif 22 <= start < 24:
                return 0.43
            elif 24 <= start < 26:
                return 0.48
            elif 26 <= start < 28:
                return 0.53
            elif 28 <= start < 30:
                return 0.57
            elif 30 <= start < 35:
                return 0.66
            elif 35 <= start < 40:
                return 0.75
            elif 40 <= start < 45:
                return 0.82
            elif 45 <= start < 50:
                return 0.89
            elif 50 <= start < 55:
                return 0.94
            elif 55 <= start < 60:
                return 1
            elif 60 <= start < 65:
                return 1.05
            elif 65 <= start < 70:
                return 1.1
            elif 70 <= start < 80:
                return 1.18
            elif 80 <= start < 90:
                return 1.25
            elif 90 <= start < 100:
                return 1.31
            elif 100 <= start < 110:
                return 1.37
            else:
                return 1.43
        elif 12 < end <= 14:
            if start < 14:
                return 0.08
            elif 14 <= start < 16:
                return 0.08
            elif 16 <= start < 18:
                return 0.16
            elif 18 <= start < 20:
                return 0.22
            elif 20 <= start < 22:
                return 0.28
            elif 22 <= start < 24:
                return 0.33
            elif 24 <= start < 26:
                return 0.38
            elif 26 <= start < 28:
                return 0.43
            elif 28 <= start < 30:
                return 0.48
            elif 30 <= start < 35:
                return 0.57
            elif 35 <= start < 40:
                return 0.65
            elif 40 <= start < 45:
                return 0.73
            elif 45 <= start < 50:
                return 0.79
            elif 50 <= start < 55:
                return 0.85
            elif 55 <= start < 60:
                return 0.91
            elif 60 <= start < 65:
                return 0.96
            elif 65 <= start < 70:
                return 1
            elif 70 <= start < 80:
                return 1.09
            elif 80 <= start < 90:
                return 1.16
            elif 90 <= start < 100:
                return 1.22
            elif 100 <= start < 110:
                return 1.28
            else:
                return 1.33
        elif 14 < end <= 16:
            if start < 14:
                return 0.07
            elif 14 <= start < 16:
                return 0.07
            elif 16 <= start < 18:
                return 0.07
            elif 18 <= start < 20:
                return 0.14
            elif 20 <= start < 22:
                return 0.22
            elif 22 <= start < 24:
                return 0.27
            elif 24 <= start < 26:
                return 0.31
            elif 26 <= start < 28:
                return 0.35
            elif 28 <= start < 30:
                return 0.39
            elif 30 <= start < 35:
                return 0.49
            elif 35 <= start < 40:
                return 0.57
            elif 40 <= start < 45:
                return 0.64
            elif 45 <= start < 50:
                return 0.71
            elif 50 <= start < 55:
                return 0.77
            elif 55 <= start < 60:
                return 0.82
            elif 60 <= start < 65:
                return 0.87
            elif 65 <= start < 70:
                return 0.92
            elif 70 <= start < 80:
                return 1
            elif 80 <= start < 90:
                return 1.07
            elif 90 <= start < 100:
                return 1.14
            elif 100 <= start < 110:
                return 1.2
            else:
                return 1.25
        elif 16 < end <= 18:
            if start < 14:
                return 0.07
            elif 14 <= start < 16:
                return 0.07
            elif 16 <= start < 18:
                return 0.07
            elif 18 <= start < 20:
                return 0.07
            elif 20 <= start < 22:
                return 0.13
            elif 22 <= start < 24:
                return 0.18
            elif 24 <= start < 26:
                return 0.23
            elif 26 <= start < 28:
                return 0.27
            elif 28 <= start < 30:
                return 0.32
            elif 30 <= start < 35:
                return 0.43
            elif 35 <= start < 40:
                return 0.49
            elif 40 <= start < 45:
                return 0.57
            elif 45 <= start < 50:
                return 0.63
            elif 50 <= start < 55:
                return 0.69
            elif 55 <= start < 60:
                return 0.75
            elif 60 <= start < 65:
                return 0.8
            elif 65 <= start < 70:
                return 0.84
            elif 70 <= start < 80:
                return 0.93
            elif 80 <= start < 90:
                return 1
            elif 90 <= start < 100:
                return 1.06
            elif 100 <= start < 110:
                return 1.12
            else:
                return 1.18
        elif 18 < end <= 20:
            if start < 14:
                return 0.06
            elif 14 <= start < 16:
                return 0.06
            elif 16 <= start < 18:
                return 0.06
            elif 18 <= start < 20:
                return 0.06
            elif 20 <= start < 22:
                return 0.06
            elif 22 <= start < 24:
                return 0.11
            elif 24 <= start < 26:
                return 0.16
            elif 26 <= start < 28:
                return 0.21
            elif 28 <= start < 30:
                return 0.25
            elif 30 <= start < 35:
                return 0.35
            elif 35 <= start < 40:
                return 0.43
            elif 40 <= start < 45:
                return 0.5
            elif 45 <= start < 50:
                return 0.57
            elif 50 <= start < 55:
                return 0.63
            elif 55 <= start < 60:
                return 0.68
            elif 60 <= start < 65:
                return 0.74
            elif 65 <= start < 70:
                return 0.78
            elif 70 <= start < 80:
                return 0.86
            elif 80 <= start < 90:
                return 0.93
            elif 90 <= start < 100:
                return 1
            elif 100 <= start < 110:
                return 1.06
            else:
                return 1.12
        elif 20 < end:
            if start < 14:
                return 0.06
            elif 14 <= start < 16:
                return 0.06
            elif 16 <= start < 18:
                return 0.06
            elif 18 <= start < 20:
                return 0.06
            elif 20 <= start < 22:
                return 0.06
            elif 22 <= start < 24:
                return 0.06
            elif 24 <= start < 26:
                return 0.1
            elif 26 <= start < 28:
                return 0.15
            elif 28 <= start < 30:
                return 0.19
            elif 30 <= start < 35:
                return 0.29
            elif 35 <= start < 40:
                return 0.37
            elif 40 <= start < 45:
                return 0.44
            elif 45 <= start < 50:
                return 0.51
            elif 50 <= start < 55:
                return 0.57
            elif 55 <= start < 60:
                return 0.62
            elif 60 <= start < 65:
                return 0.67
            elif 65 <= start < 70:
                return 0.72
            elif 70 <= start < 80:
                return 0.8
            elif 80 <= start < 90:
                return 0.87
            elif 90 <= start < 100:
                return 0.94
            elif 100 <= start < 110:
                return 1
            else:
                return 1.07

    def define_tree_resist(self, size, width):
        if self.tree == "Берёза":
            resistivity = (5.1 * (10 ** 16)) / 100  # Удельное сопротивление березы, Ом * м
        else:
            resistivity = (2.3 * (10 ** 15)) / 100  # Удельное сопротивление сосны, Ом * м
        sq_area = (size * width) * 0.000001 # Площадь сечения между электродами, м2
        l = 0.02 # Расстояние между электродами в сушильной камере, м
        return int((resistivity * l) / sq_area)

a = Tree("Берёза", "Нормальный", 18, 33,77, 9)
print(a.steps)
print(a.category)
print(a.ventSpeed)
print(a.stages)



