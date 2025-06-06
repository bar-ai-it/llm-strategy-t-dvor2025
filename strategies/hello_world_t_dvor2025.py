class Strategy:
    def __init__(self, client):
        self.name = "Hello World T-dvor2025"
        self.client = client
        self.minutes = []
        self.history_count = 30 # 30 уникальных минут в self.minutes
        self.position = {"avg_price": 0, "lots": 0 } #lots 0 - нет позиции, 1 - открыта, -1 - закрыта? avg_price - средняя цена позиции

    def update(self, marketdata):
        #market data https://tinkoff.github.io/investAPI/marketdata/#marketdataresponse
        print(marketdata)

        #получаем данные из marketdata в current_minute
        current_minute = {"minute": '2025-01-01 00:00:00', "price": 100, "vol": 10}

        #обрабатываем логику только при смене минуты
        if self.minutes[-1]["minute"] != current_minute["minute"]:
            #добавляем новую минуту
            self.minutes.append(current_minute)
            #оставляем только нужно кол-во минут
            if len(self.minutes) > self.history_count:
                self.minutes.pop(0)

        self.work()
        return

    def position_get(self):
        #тут реализуем логику получения позиции из текущего состояния, а так же из api
        print("currect position")
        return self.position

    def position_open(self, type, price, lots):
        #тут реализуем логику открытия позиции в api
        print("open position")
        if type == "long":
            self.position = {"avg_price": price, "lots": lots }
        else:
            self.position = {"avg_price": price, "lots": -lots }

    def position_close(self):
        #тут реализуем логику закрытия позиции в api
        print("close position")
        self.position = {"avg_price": 0, "lots": 0 }

    #функция которая будет на основе данных self.minutes принимать решения о покупке/продаже
    def work(self):



        return