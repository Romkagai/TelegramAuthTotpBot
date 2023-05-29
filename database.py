import sqlite3


# Функции для работы с базой данных
# Стартовая функция: создание базы данных в случае её отсутствия
def create_or_check_database():
    conn = sqlite3.connect('user_codes.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS codes(userid INT, CODE1 TEXT, CODE2 TEXT, CODE3 TEXT, CODE4 TEXT, CODE5 TEXT);")
    cur.execute("CREATE TABLE IF NOT EXISTS names(userid INT, NAME1 TEXT, NAME2 TEXT, NAME3 TEXT, NAME4 TEXT, NAME5 TEXT);")
    conn.commit()


# Подключение к базе данных
def connect_to_database():
    conn = sqlite3.connect('user_codes.db')
    return conn


# Добавление собственного имени для сервиса
def add_service_name_to_db(text, userid, column_number):
    column_number = str(int(column_number) + 1)
    conn = connect_to_database()
    cur = conn.cursor()
    query = f"UPDATE names SET NAME{column_number} = ? WHERE userid = ?;"
    cur.execute(query, (text, userid,))
    conn.commit()
    conn.close()


# Добавление собственного ключа в базу данных
def add_key_to_db(text, user_id, column_number):
    column_number = str(int(column_number) + 1)
    conn = connect_to_database()
    cur = conn.cursor()
    query = f"UPDATE codes SET CODE{column_number} = ? WHERE userid = ?;"
    cur.execute(query, (text, user_id,))
    conn.commit()
    conn.close()


# Удаление ключа из базы данных
def remove_key_from_db(user_id, column_number):
    column_number = str(int(column_number) + 1)
    conn = connect_to_database()
    cur = conn.cursor()
    query = f"UPDATE codes SET CODE{column_number} = NULL WHERE userid = ?;"
    cur.execute(query, (user_id,))
    conn.commit()
    conn.close()


# Взятие ключа из базы данных
def get_key_from_db(userid, column_number):
    column_number = str(int(column_number) + 1)
    conn = connect_to_database()
    cur = conn.cursor()
    query = f"SELECT CODE{column_number} FROM codes WHERE userid = ?;"
    current_key = cur.execute(query, (userid,))
    current_key = current_key.fetchone()
    conn.close()
    return current_key


# Взятие имени сервиса из базы данных
def get_service_name_from_db(userid, column_number):
    column_number = str(int(column_number) + 1)
    conn = connect_to_database()
    cur = conn.cursor()
    query = f"SELECT NAME{column_number} FROM names WHERE userid = ?;"
    current_name = cur.execute(query, (userid,))
    current_name = current_name.fetchone()
    conn.close()
    return current_name


# Взятие всех имен сервисов из базы данных
def get_service_names(userid):
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute('SELECT NAME1, NAME2, NAME3, NAME4, NAME5 FROM names WHERE userid = ?;', (userid,))
    rows = cur.fetchall()
    conn.close()
    return rows[0] if rows else None


# Проверка наличия нового юзера в базе данных
def check_new_user(id):
    conn = connect_to_database()
    cur = conn.cursor()
    check_user = cur.execute('select userid from codes where userid = ?', (id,))
    if check_user.fetchone() is None:
        cur.execute('insert into codes(userid, CODE1, CODE2, CODE3, CODE4, CODE5) VALUES(?, ?, ?, ?, ?, ?);',
                    (id, None, None, None, None, None))
        cur.execute('insert into names(userid, NAME1, NAME2, NAME3, NAME4, NAME5) VALUES(?, ?, ?, ?, ?, ?);',
                    (id, 'Сервис 1', 'Сервис 2', 'Сервис 3', 'Сервис 4', 'Сервис 5'))
        conn.commit()
    conn.close()
