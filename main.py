import os

import psycopg2
import dotenv

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients
            (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(30) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR(50) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS phone_numbers
            (
            phone_number VARCHAR(20) NOT NULL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            CONSTRAINT fk_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            );
            """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones: list = None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id;
            """, (first_name, last_name, email))
        client_id = cur.fetchone()
        if not phones is None:
            for phone in phones:
                add_phone(conn, phone, client_id)

def add_phone(conn, phone_number, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phone_numbers (phone_number, client_id) VALUES (%s, %s);
            """, (phone_number, client_id))
        try:
            conn.commit()
        except:
            pass

def update_client(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                SELECT 
                    first_name, 
                    last_name, 
                    email
                FROM clients
                WHERE id = %s 
                """, tuple(client_id))
            client = cur.fetchone()
            first_name = client[0] if first_name is None else first_name
            last_name = client[1] if last_name is None else last_name
            email = client[2] if email is None else email
            cur.execute("""
                UPDATE clients SET 
                    first_name = %s, 
                    last_name = %s, 
                    email = %s
                WHERE id = %s
                """, (first_name, last_name, email, client_id))
            conn.commit()
        except:
            pass

def delete_phone(conn, phone_number):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                DELETE FROM phone_numbers WHERE phone_number = %s;
                """, (phone_number,))
            conn.commit()
        except:
            pass

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                DELETE FROM clients WHERE id = %s;
                """, (client_id,))
            conn.commit()
        except:
            pass

def find_client(conn, /, *, first_name=None, last_name=None, email=None, phone=None):
    conditions_list = list()
    if not first_name is None:
        conditions_list.append(f"first_name = '{first_name}'")
    if not last_name is None:
        conditions_list.append(f"last_name = '{last_name}'")
    if not email is None:
        conditions_list.append(f"email = '{email}'")
    if not phone is None:
        conditions_list.append(f"id = (SELECT client_id FROM phone_numbers WHERE phone_number = '{phone}')")
    if len(conditions_list) < 0:
        return
    conditions = ' AND '.join(conditions_list)
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM clients c WHERE {conditions};")
        return cur.fetchall()

if __name__ == "__main__":
    dotenv.load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        create_tables(conn)

        add_client(conn, 'Петр', 'Петров', 'petrov@gmail.com', ['89036745677', '11111111111', '89026713454'])
        add_client(conn, 'Сидоров', 'Василий', 'sidorov@gmail.com', ['89047251324'])
        add_client(conn, 'Иванов', 'Иван', 'ivanov@gmail.com', ['89784056780'])

        add_phone(conn, '89063445695', 2)
        delete_phone(conn, '11111111111')

        delete_client(conn, 3)

        print(find_client(conn, last_name='Петров'))