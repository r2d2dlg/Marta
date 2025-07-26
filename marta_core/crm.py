import psycopg2
import os
import datetime

class CRM:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT", "5432")
        )
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone_number VARCHAR(50),
                company VARCHAR(255),
                notes TEXT,
                last_contact TIMESTAMP
            );
            """)
            self.conn.commit()

    def add_client(self, client):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO clients (name, email, phone_number, company, notes, last_contact)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING;
                """,
                (client.name, client.email, client.phone_number, client.company, client.notes, client.last_contact)
            )
            self.conn.commit()

    def get_client(self, email):
        with self.conn.cursor() as cur:
            cur.execute("SELECT name, email, phone_number, company, notes, last_contact FROM clients WHERE email = %s;", (email,))
            row = cur.fetchone()
            if row:
                client = Client(name=row[0], email=row[1], phone_number=row[2], company=row[3])
                client.notes = row[4]
                client.last_contact = row[5]
                return client
            return None

    def update_client(self, email, notes):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE clients SET notes = %s, last_contact = %s WHERE email = %s;",
                (notes, datetime.datetime.now(), email)
            )
            self.conn.commit()

class Client:
    def __init__(self, name, email, phone_number, company=None):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.company = company
        self.notes = ""
        self.last_contact = None

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "company": self.company,
            "notes": self.notes,
            "last_contact": self.last_contact.isoformat() if self.last_contact else None,
        }