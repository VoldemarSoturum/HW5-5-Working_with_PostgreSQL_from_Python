# 📇 Клиентская база на PostgreSQL

Python-скрипт для управления клиентами и их телефонами с валидацией email и номеров телефонов.

---

## 📦 Зависимости

Установите необходимые библиотеки:

```bash
pip install psycopg2 email-validator phonenumbers
```

---

## 🛠 Настройки подключения к базе данных

По умолчанию используется:

```python
dbname="netology_db"
user="postgres"
password="postgres"
host="localhost"
port="5432"
```

🔧 Измените параметры при необходимости в функции `main()`.

---

## 🗄 Создание базы данных

Создайте базу данных `netology_db`, если ещё не создана:

```bash
psql -U postgres
CREATE DATABASE netology_db;
```

---

## 🚀 Запуск

```bash
python client_manager.py
```

Замените `client_manager.py` на имя вашего файла.

---

## 📋 Меню программы

```text
📋 Меню:
1. Создать структуру БД
2. Добавить клиента
3. Добавить телефон
4. Обновить данные клиента
5. Удалить телефон клиента
6. Удалить клиента
7. Найти клиента
8. Показать всех клиентов
0. Выход
```

---

## 🧪 Валидация данных

- ✅ **Email** — проверяется с помощью библиотеки `email-validator`
- 📞 **Телефон** — форматируется в международный формат через `phonenumbers` и требует выбора региона
- 📏 Все поля обрезаются и не допускают пустые значения или значения длиннее ограничения базы данных

---

## ⚠️ Возможные ошибки

- `❗ Ошибка: значение слишком длинное для одного из полей`  
  → Убедитесь, что значения (например, телефон) не превышают длину поля в БД

- `❌ Неверный email`  
  → Введите корректный email, например `user@example.com`

- `❌ Номер телефона некорректен`  
  → Введите номер без кода страны (например, `9123456789`) и выберите страну

---

## 📁 Структура таблиц

- `clients` — имя, фамилия, email
- `phones` — один или несколько телефонов, связанных с `clients`

---

## 📌 Автор

Разработано как проект для практики с Python, PostgreSQL и библиотеками валидации.
