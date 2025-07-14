# Домашнее задание «Работа с PostgreSQL из Python»


# Задание

# Создайте программу для управления клиентами на Python.Требуется хранить персональную информацию о клиентах:

#     имя
#     фамилия
#     email
#     телефон

# Сложность в том, что телефон у клиента может быть не один, а два, три и даже больше. А может и вообще не быть телефона, например, он не захотел его оставлять.

# Вам необходимо разработать структуру БД для хранения информации и несколько функций на Python для управления данными.

#     Функция, создающая структуру БД (таблицы).
#     Функция, позволяющая добавить нового клиента.
#     Функция, позволяющая добавить телефон для существующего клиента.
#     Функция, позволяющая изменить данные о клиенте.
#     Функция, позволяющая удалить телефон для существующего клиента.
#     Функция, позволяющая удалить существующего клиента.
#     Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.

# Функции выше являются обязательными, но это не значит, что должны быть только они. При необходимости можете создавать дополнительные функции и классы.

# Также предоставьте код, демонстрирующий работу всех написанных функций.

# Результатом работы будет .py файл.




import psycopg2
import re
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

REGIONS = {
    "1": "RU",  # Россия
    "2": "US",  # США
    "3": "UA",  # Украина
    "4": "BY",  # Беларусь
}

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS phones; DROP TABLE IF EXISTS clients;")
        cur.execute("""
            CREATE TABLE clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL CHECK (TRIM(first_name) <> ''),
                last_name VARCHAR(50) NOT NULL CHECK (TRIM(last_name) <> ''),
                email VARCHAR(100) UNIQUE NOT NULL CHECK (TRIM(email) <> '')
            );
        """)
        cur.execute("""
            CREATE TABLE phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                phone VARCHAR(20) NOT NULL CHECK (TRIM(phone) <> '')
            );
        """)
        conn.commit()
        print("☠️ База данных создана.")

def select_region():
    print("Выберите регион:")
    for k, v in REGIONS.items():
        print(f"{k}. {v}")
    choice = input("Ваш выбор: ").strip()
    if choice in REGIONS:
        return REGIONS[choice]
    else:
        print("☢️ Неверный выбор региона.")
        return None

def input_phone_number():
    region_code = select_region()
    if not region_code:
        return None

    local_number = input("Введите номер телефона (без кода страны, например 9123456789): ").strip()

    try:
        parsed_number = phonenumbers.parse(local_number, region_code)
        if not phonenumbers.is_valid_number(parsed_number):
            print("☢️ Номер телефона некорректен.")
            return None
        international_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return international_number
    except NumberParseException:
        print("☢️ Неверный формат номера.")
        return None

def is_valid_email(email):
    try:
        validate_email(email)  # Если email невалиден — будет исключение
        return True
    except EmailNotValidError as e:
        print(f"☢️ Неверный email: {e}")
        return False

def add_client(conn):
    first = input("Имя (не пустое): ")
    last = input("Фамилия (не пустое): ")
    email = input("Email (не пустое): ")
    MAX_PHONE_LENGTH = 20  # как в БД

    # Проверка: имя, фамилия и email не могут быть пустыми
    if not first.strip() or not last.strip() or not email.strip():
        print("☢️ Имя, фамилия и email обязательны.")
        return

    if not is_valid_email(email):
        print("☢️ Неверный формат email.")
        return

    phone_list = []
    add_phone_choice = input("Хотите оставить контактный телефон? (y/n): ").strip().lower()
    if add_phone_choice == 'y':
        while True:
            international_number = input_phone_number()
            if international_number:
                phone_list.append(international_number)
            more = input("Добавить ещё номер? (y/n): ").strip().lower()
            if more != 'y':
                break

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s) RETURNING id;
        """, (first, last, email))
        client_id = cur.fetchone()[0]

        for phone in phone_list:
            if not phone:
                print("☢️ Пустой телефон не будет добавлен.")
                continue
            if len(phone) > MAX_PHONE_LENGTH:
                print(f"☢️ Телефон слишком длинный: '{phone}' (максимум {MAX_PHONE_LENGTH} символов).")
                continue

            cur.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s);", (client_id, phone))

        conn.commit()
        print(f"☠️ Клиент {first} {last} добавлен с ID {client_id}.")

def add_phone(conn):
    client_id = input("ID клиента: ").strip()
    phone = input_phone_number()
    if not phone:
        print("☢️ Телефон не был добавлен из-за ошибки.")
        return

    with conn.cursor() as cur:
        cur.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s);", (client_id, phone))
        conn.commit()
        print("☠️ Телефон добавлен.")

def update_client(conn):
    client_id = input("ID клиента: ").strip()
    first = input("Новое имя (оставь пустым, если не менять): ").strip()
    last = input("Новая фамилия (оставь пустым, если не менять): ").strip()
    email = input("Новый email (оставь пустым, если не менять): ").strip()

    if first and not first.strip():
        print("☢️ Имя не может быть пустым.")
        return
    if last and not last.strip():
        print("☢️ Фамилия не может быть пустой.")
        return
    if email and not email.strip():
        print("☢️ Email не может быть пустым.")
        return

    if email and not is_valid_email(email):
        return

    with conn.cursor() as cur:
        if first:
            cur.execute("UPDATE clients SET first_name = %s WHERE id = %s;", (first, client_id))
        if last:
            cur.execute("UPDATE clients SET last_name = %s WHERE id = %s;", (last, client_id))
        if email:
            cur.execute("UPDATE clients SET email = %s WHERE id = %s;", (email, client_id))
        conn.commit()
        print("☠️ Данные клиента обновлены.")

def delete_phone(conn):
    client_id = input("ID клиента: ").strip()
    phone = input("Телефон для удаления: ").strip()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM phones WHERE client_id = %s AND phone = %s;", (client_id, phone))
        conn.commit()
        print("☠️ Телефон удалён.")

def delete_client(conn):
    client_id = input("ID клиента для удаления: ").strip()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
        conn.commit()
        print("☠️ Клиент удалён.")

def find_client(conn):
    print("Введите параметры поиска (можно оставить пустыми):")
    first = input("Имя: ").strip()
    last = input("Фамилия: ").strip()
    email = input("Email: ").strip()
    phone = input("Телефон: ").strip()

    query = """
        SELECT c.id, c.first_name, c.last_name, c.email, p.phone
        FROM clients c
        LEFT JOIN phones p ON c.id = p.client_id
        WHERE TRUE
    """
    params = []
    if first:
        query += " AND c.first_name = %s"
        params.append(first)
    if last:
        query += " AND c.last_name = %s"
        params.append(last)
    if email:
        query += " AND c.email = %s"
        params.append(email)
    if phone:
        query += " AND p.phone = %s"
        params.append(phone)

    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        if not rows:
            print("☢️ Клиенты не найдены.")
        else:
            print("🧿 Найдено:")
            for row in rows:
                print(row)

def show_all_clients(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, COALESCE(string_agg(p.phone, ', '), '—') AS phones
            FROM clients c
            LEFT JOIN phones p ON c.id = p.client_id
            GROUP BY c.id
            ORDER BY c.id;
        """)
        rows = cur.fetchall()
        if not rows:
            print("☢️ В базе данных нет клиентов.")
        else:
            print("📜 Список всех клиентов:")
            for row in rows:
                client_id, first_name, last_name, email, phones = row
                print(f"ID: {client_id}, {first_name} {last_name}, Email: {email}, Телефоны: {phones}")

# Меню для взаимодействия с пользователем
def main():
    # Установrf соединение с базой данных PostgreSQL
    conn = psycopg2.connect(
        dbname="netology_db",   # Название базы данных
        user="postgres",        # Имя пользователя
        password="postgres",    # Пароль пользователя
        host="localhost",       # Хост базы данных (Docker обычно использует localhost)
        port="5432"             # Порт PostgreSQL (по умолчанию 5432)
    )

    while True:
        print("\n📜 Меню:")
        print("1. Создать структуру БД")
        print("2. Добавить клиента")
        print("3. Добавить телефон")
        print("4. Обновить данные клиента")
        print("5. Удалить телефон клиента")
        print("6. Удалить клиента")
        print("7. Найти клиента")
        print("8. Показать всех клиентов")
        print("0. Выход")

        choice = input("Выбор: ").strip()

        try:
            if choice == "1":
                create_db(conn)
            elif choice == "2":
                add_client(conn)
            elif choice == "3":
                add_phone(conn)
            elif choice == "4":
                update_client(conn)
            elif choice == "5":
                delete_phone(conn)
            elif choice == "6":
                delete_client(conn)
            elif choice == "7":
                find_client(conn)
            elif choice == "8":
                show_all_clients(conn)
            elif choice == "0":
                print("🤘 Завершение работы.")
                break
            else:
                print("💀 Неверный выбор.")
        except psycopg2.errors.StringDataRightTruncation:
            print("☢️ Ошибка: значение слишком длинное для одного из полей.")
        except Exception as e:
            print("☢️ Другая ошибка:", e)


if __name__ == "__main__":
    main()
