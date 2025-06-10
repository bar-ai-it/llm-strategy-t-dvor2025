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
        # Проверка достаточности данных для расчета RSI
        if len(self.minutes) < 15:
            return
        
        # Получение текущей цены
        current_price = self.minutes[-1]["price"]
        
        # Проверка условий закрытия позиции
        position = self.position_get()
        if position["lots"] != 0:
            # Для лонг-позиции
            if position["lots"] > 0:
                if current_price <= position["avg_price"] * 0.98:  # Стоп-лосс 2%
                    self.position_close()
                elif current_price >= position["avg_price"] * 1.04:  # Тейк-профит 4%
                    self.position_close()
            
            # Для шорт-позиции
            elif position["lots"] < 0:
                if current_price >= position["avg_price"] * 1.02:  # Стоп-лосс 2%
                    self.position_close()
                elif current_price <= position["avg_price"] * 0.96:  # Тейк-профит 4%
                    self.position_close()
            return
        
        # Расчет RSI за 14 периодов
        prices = [m["price"] for m in self.minutes[-15:]]
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Проверка условий открытия позиции
        if rsi < 30:
            self.position_open("long", current_price, 1)  # Открытие лонг-позиции
        elif rsi > 70:
            self.position_open("short", current_price, 1)  # Открытие шорт-позиции
```

## Запуск

Скрипт выведет доступные счета для текущего токена

- python main.py


Запуск торговли 1 лотом фонда TPAY ~100р.

- python main.py --account 123456789



