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

    #функция которая будет возвращать позицию
    def position_get(self):
        print("currect position")
        return self.position

    def position_open(self, type, price, lots):
        print("open position")
        if type == "long":
            self.position = {"avg_price": price, "lots": lots }
        else:
            self.position = {"avg_price": price, "lots": -lots }

    def position_close(self):
        print("close position")
        self.position = {"avg_price": 0, "lots": 0 }

    #функция которая будет на основе данных self.minutes принимать решения о покупке/продаже
    def work(self):
        # Если недостаточно данных для расчета RSI, выходим
        if len(self.minutes) < 15:
            return

        # Получаем текущую цену из последней минуты
        current_price = self.minutes[-1]["price"]

        # Проверяем условия для закрытия позиции (если она открыта)
        position = self.position_get()
        if position["lots"] != 0:
            # Для лонг-позиции
            if position["lots"] > 0:
                # Проверка стоп-лосса (2%)
                if current_price <= position["avg_price"] * 0.98:
                    self.position_close()
                # Проверка тейк-профита (4%)
                elif current_price >= position["avg_price"] * 1.04:
                    self.position_close()

            # Для шорт-позиции
            elif position["lots"] < 0:
                # Проверка стоп-лосса (2%)
                if current_price >= position["avg_price"] * 1.02:
                    self.position_close()
                # Проверка тейк-профита (4%)
                elif current_price <= position["avg_price"] * 0.96:
                    self.position_close()
            return

        # Рассчитываем RSI
        prices = [m["price"] for m in self.minutes[-15:]]
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Проверяем условия для открытия позиции
        if rsi < 30:
            # Покупаем (открываем лонг)
            self.position_open("long", current_price, 1)
        elif rsi > 70:
            # Продаем (открываем шорт)
            self.position_open("short", current_price, 1)