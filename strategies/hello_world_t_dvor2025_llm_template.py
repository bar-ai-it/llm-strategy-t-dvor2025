import asyncio
from uuid import uuid4
import time
from tinkoff.invest import AsyncClient
from decimal import Decimal
from datetime import timedelta
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
from tinkoff.invest import Client, OrderDirection, Quotation, OrderType, PostOrderResponse, OrderState
from tinkoff.invest.schemas import OrderDirection, OrderType, PostOrderAsyncRequest
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.schemas import CandleSource
from tinkoff.invest.utils import now


class Strategy:
    def __init__(self, client, instrument, work_account):
        self.name = "Hello World T-dvor2025"
        self.client = client
        self.minutes = []
        self.history_count = 30 # 30 уникальных минут в self.minutes
        self.position = {"avg_price": 0, "lots": 0 } #lots 0 - нет позиции, 1 - открыта, -1 - закрыта? avg_price - средняя цена позиции
        self.instrument = instrument
        self.work_account = work_account
        self.last_trade = time.time()

        #загружаем данные из истории
        with Client(self.client._token, app_name=self.client._app_name) as client:
            for candle in client.get_all_candles(
                    instrument_id=self.instrument,
                    from_=now() - timedelta(minutes=self.history_count * 3), #могут быть пропущены данные
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
                    candle_source_type=CandleSource.CANDLE_SOURCE_UNSPECIFIED,
            ):
                # print(candle)
                current_minute = {
                    "minute": candle.time.strftime('%Y-%m-%d %H:%M:%S'),
                    "price": str(quotation_to_decimal(candle.close)),
                    "vol": candle.volume
                }
                # обрабатываем логику только при смене минуты
                if not self.minutes or self.minutes[-1]["minute"] != current_minute["minute"]:
                    # добавляем новую минуту
                    self.minutes.append(current_minute)

        return


    async def update(self, marketdata):
        #market data https://tinkoff.github.io/investAPI/marketdata/#marketdataresponse
        # print(marketdata.candle)

        if not marketdata.candle:
            return

        #получаем данные из marketdata в current_minute
        current_minute = {
            "minute": marketdata.candle.time.strftime('%Y-%m-%d %H:%M:%S'),
            "price": str(quotation_to_decimal(marketdata.candle.close)),
            "vol": marketdata.candle.volume
        }
        #обрабатываем логику только при смене минуты
        if not self.minutes or self.minutes[-1]["minute"] != current_minute["minute"]:
            #добавляем новую минуту
            self.minutes.append(current_minute)
            #оставляем только нужно кол-во минут
            while len(self.minutes) > self.history_count:
                self.minutes.pop(0)

            print(current_minute)

            self.work()
        else:
            self.minutes[-1] = current_minute


        # Пример работы
        # Покупка
        # await self.position_open('long', marketdata.candle.close, 1)
        # await self.position_open('long', decimal_to_quotation(Decimal(10.0)), 1) # покупка по фиксированной цене 10р
        # продажа
        # await self.position_open('short', marketdata.candle.close, 1)
        # await self.position_open('short', decimal_to_quotation(Decimal(10.0)), 1) # продажа по фиксированной цене 10р
        # закрытие текущей позиции
        # await self.position_close()

        return

    def position_get(self):
        #тут реализуем логику получения позиции из текущего состояния, а так же из api
        # print("currect position")
        return self.position

    async def position_open(self, type, price, lots):
        #Если позиция уже открыта ее нужно закрыть
        # position = self.position_get()
        # if position and position["lots"] != 0:
        #     print("close position before open")
        #     await self.position_close()

        # сделаем примитивную защиту чтобы позиции не открывались чаще раза в 30 секунд
        if time.time() - self.last_trade < 30:
            print("Подождите 30 секунд с момента последнего открытия позиции")
            return

        #тут реализуем логику открытия позиции в api
        if type == "long":
            print("Открываем позицию в long")
            with Client(self.client._token, app_name=self.client._app_name) as client:
                self.last_trade = time.time()
                response = client.orders.post_order(
                    figi=self.instrument,
                    quantity=lots,
                    price=price,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    account_id=self.work_account["id"],
                    # order_type=OrderType.ORDER_TYPE_MARKET, #будет исполено сразу, без ожидания исполнения
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                    order_id=str(uuid4()),
                )
            print(response)

            #здесь нужно получать цену исполнения, а не запрошенную, для упрощения мы так же не будем ждать исполнения, а просто запишем цену в position
            #Если была позиция не нулевая, хорошо бы высчитать средневзвешанную цену, но пока просто запишем цену
            self.position = {"avg_price": quotation_to_decimal(price), "lots": self.position["lots"]+ lots }
        else:
            print("Открываем позицию в short")

            with Client(self.client._token, app_name=self.client._app_name) as client:
                self.last_trade = time.time()
                response = client.orders.post_order(
                    figi=self.instrument,
                    quantity=lots,
                    price=price,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    account_id=self.work_account["id"],
                    # order_type=OrderType.ORDER_TYPE_MARKET, #будет исполено сразу, без ожидания исполнения
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                    order_id=str(uuid4()),
                )
            print(response)

            self.position = {"avg_price": quotation_to_decimal(price), "lots": self.position["lots"] - lots }


    async def position_close(self):
        #тут реализуем логику закрытия позиции в api
        print("закрываем позицию")

        position = self.position_get()

        if position and position["lots"] !=0:

            if self.position["lots"] > 0:
                with Client(self.client._token, app_name=self.client._app_name) as client:
                    response = client.orders.post_order(
                        figi=self.instrument,
                        quantity=self.position["lots"],
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        account_id=self.work_account["id"],
                        order_type=OrderType.ORDER_TYPE_MARKET, #будет исполено сразу, без ожидания исполнения
                        # order_type=OrderType.ORDER_TYPE_LIMIT,
                        order_id=str(uuid4()),
                    )
                    print(response)
            elif self.position["lots"] < 0:
                with Client(self.client._token, app_name=self.client._app_name) as client:
                    response = client.orders.post_order(
                        figi=self.instrument,
                        quantity=abs(self.position["lots"]),
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        account_id=self.work_account["id"],
                        order_type=OrderType.ORDER_TYPE_MARKET, #будет исполено сразу, без ожидания исполнения
                        # order_type=OrderType.ORDER_TYPE_LIMIT,
                        order_id=str(uuid4()),
                    )
                    print(response)
                return

            self.position = {"avg_price": 0, "lots": 0 }

    #функция которая будет на основе данных self.minutes принимать решения о покупке/продаже
    def work(self):
        return