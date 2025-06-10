import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import argparse

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)
from tinkoff.invest import Client
from strategies.hello_world_t_dvor2025 import Strategy #импортируем стратегию

#Парсим аргументы командной строки
parser = argparse.ArgumentParser(
    description="Hello world T-Dvor 2025"
)
parser.add_argument("--account", "-a", type=str, help="номер счета")
args = parser.parse_args()

#Загружаем переменные окружения
load_dotenv(Path(os.getcwd()).resolve() / ".env")

TOKEN = os.environ["INVEST_TOKEN"]
# INSTRUMENT_FOR_TRADE = os.environ["INSTRUMENT_FOR_TRADE"]
INSTRUMENT_FOR_TRADE = "TCS00A108WX3" #figi для TPAY  https://developer.tbank.ru/invest/intro/intro/faq_identification

accounts = []
work_account = {}

with Client(TOKEN) as client:
    response = client.users.get_accounts()
    for account in response.accounts:  # Доступ к списку счетов
        # выводим только доступные счета
        if account.status == 2:
            accounts.append({"id":account.id, "name":account.name})
            if args.account == account.id:
                work_account = {"id":account.id, "name":account.name}
                break

if not args.account or not work_account:
    print("Необходимо указать номер счета при запуске бота с параметром из списка ниже, например --account 123456789\n")
    print("Доступные счета (account name)")
    for account in accounts:
        print(f"{account['id']} {account['name']}")
    #Выводим список брокерских счетов
    exit(1)

#Запускаем бота на заданном счете
print(f"Бот запущен на счете: {work_account['id']} ({work_account['name']})")

#Дальше работает в асинхронном режиме
async def main():
    async def request_iterator():
        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=[
                    CandleInstrument(
                        figi=INSTRUMENT_FOR_TRADE,
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    )
                ],
            )
        )
        while True:
            await asyncio.sleep(1)

    hello_strategy = Strategy(AsyncClient(TOKEN), INSTRUMENT_FOR_TRADE, work_account)

    async with AsyncClient(TOKEN) as client:

        async for marketdata in client.market_data_stream.market_data_stream(
            request_iterator()
        ):
            await hello_strategy.update(marketdata)


if __name__ == "__main__":
    asyncio.run(main())