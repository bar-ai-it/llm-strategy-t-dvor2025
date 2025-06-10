# Hello world для LLM/GPT кодирования стратегий

Скрипт запуска торгового инструмента, например CNURUBF через API Т-Инвестиций

Пример программы hello world для алготрейдера на выступлении в https://t-dvor.ru/

## Токен

Токен получаем в разделе безопасности https://www.tbank.ru/mybank/profile/security/

Выбираем счет и указываем полный доступ.

Сохраняем в файле проекта .env заменив им слово ТОКЕН 
```
INVEST_TOKEN=ТОКЕН
```


## Установка
- Python 3.9+

```
pip install -r requirements.txt
```


## Создаем торговую стратегию через LLM / Gpt модели

Промпт для https://chat.deepseek.com

```
Создай код на python для стратегии: при RSI < 30 – покупай, RSI > 70 – продавай, стоп-лосс 2%, тейк-профит 4%

Напиши функцию work в классе Strategy.

Текущая история лежит в  self.minutes длинной self.history_count минут.
Функция открыть позицию - position_open.
Функция закрыть позицию -  position_close.
Функция получения наличия или отсутствия позиции -  position_get

Ниже код класса:
ниже код из класса Strategy, файл: strategies/hello_world_t_dvor2025.py
```

Результат сохранен в strategies/hello_world_t_dvor2025_llmresult.py


# Реализация торговой стратегии на Python

## Стратегия
- **Покупать (лонг)** при RSI < 30
- **Продавать (шорт)** при RSI > 70
- **Стоп-лосс**: 2% от цены входа
- **Тейк-профит**: 4% от цены входа

## Код реализации

```python
class Strategy:
    def __init__(self, client):
        self.name = "Hello World T-dvor2025"
        self.client = client
        self.minutes = []
        self.history_count = 30
        self.position = {"avg_price": 0, "lots": 0}

    # ... (остальные методы класса остаются без изменений)

        def work(self):
        # Параметры стратегии
        period = 14  # период RSI
        stop_loss_pct = 0.02  # 2%
        take_profit_pct = 0.04  # 4%

        # Проверяем достаточность истории
        if len(self.minutes) < period + 1:
            return

        # Вытаскиваем цены закрытия
        closes = [float(m["price"]) for m in self.minutes]

        # Вычисляем изменения
        gains = []
        losses = []
        for i in range(1, period + 1):
            change = closes[-i] - closes[-i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        # Средние приросты и потери
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        current_price = closes[-1]
        pos = self.position_get()

        # Логика входа
        if pos["lots"] == 0 and rsi < 30:
            price_q = decimal_to_quotation(Decimal(current_price))
            asyncio.create_task(self.position_open('long', price_q, 1))
            return

        # Логика выхода по стоп-лосс, тейк-профит или RSI
        if pos["lots"] > 0:
            entry_price = pos["avg_price"]
            # стоп-лосс
            if current_price <= entry_price * (1 - stop_loss_pct):
                asyncio.create_task(self.position_close())
                return
            # тейк-профит
            if current_price >= entry_price * (1 + take_profit_pct):
                asyncio.create_task(self.position_close())
                return
            # перекупленность
            if rsi > 70:
                asyncio.create_task(self.position_close())
                return
```

## Запуск

Скрипт выведет доступные счета для текущего токена

- python main.py


Запуск торговли 1 лотом фонда TPAY ~100р.

- python main.py --account 123456789



