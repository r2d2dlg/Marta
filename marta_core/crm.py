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
        self.create_sales_funnel_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                position VARCHAR(255),
                email VARCHAR(255) UNIQUE NOT NULL,
                phone_number VARCHAR(50),
                company VARCHAR(255),
                notes TEXT,
                last_contact TIMESTAMP,
                last_contact_source VARCHAR(50),
                ai_insights JSONB
            );
            """)
            self.conn.commit()

    def create_sales_funnel_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sales_funnel (
                id SERIAL PRIMARY KEY,
                client_id INTEGER UNIQUE NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
                stage VARCHAR(255) NOT NULL CHECK (stage IN ('Lead', 'Contacted', 'Proposal', 'Negotiation', 'Won', 'Lost')),
                status VARCHAR(255) NOT NULL,
                notes TEXT,
                estimated_value NUMERIC(10, 2),
                close_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            self.conn.commit()

    def add_client(self, client):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO clients (first_name, last_name, position, email, phone_number, company, notes, last_contact, last_contact_source, ai_insights)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING;
                """,
                (client.first_name, client.last_name, client.position, client.email, client.phone_number, client.company, client.notes, client.last_contact, client.last_contact_source, client.ai_insights)
            )
            self.conn.commit()

    def get_client(self, email):
        with self.conn.cursor() as cur:
            cur.execute("SELECT first_name, last_name, position, email, phone_number, company, notes, last_contact, last_contact_source, ai_insights FROM clients WHERE email = %s;", (email,))
            row = cur.fetchone()
            if row:
                client = Client(first_name=row[0], last_name=row[1], position=row[2], email=row[3], phone_number=row[4], company=row[5])
                client.notes = row[6]
                client.last_contact = row[7]
                client.last_contact_source = row[8]
                client.ai_insights = row[9]
                return client
            return None

    def update_client(self, email, data):
        with self.conn.cursor() as cur:
            fields = []
            values = []
            for key, value in data.items():
                fields.append(f"{key} = %s")
                values.append(value)
            
            values.append(email)

            cur.execute(
                f"UPDATE clients SET {', '.join(fields)}, last_contact = %s WHERE email = %s;",
                values + [datetime.datetime.now()]
            )
            self.conn.commit()

    def get_all_sales_funnel_entries(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT sf.id, c.company, sf.stage, sf.status, sf.notes, sf.estimated_value, sf.close_date
                FROM sales_funnel sf
                JOIN clients c ON sf.client_id = c.id;
            """)
            return cur.fetchall()

    def get_sales_funnel_entry(self, company_name):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT sf.id, c.company, sf.stage, sf.status, sf.notes, sf.estimated_value, sf.close_date
                FROM sales_funnel sf
                JOIN clients c ON sf.client_id = c.id
                WHERE c.company = %s;
            """, (company_name,))
            return cur.fetchone()

    def add_sales_funnel_entry(self, data):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sales_funnel (client_id, stage, status, notes, estimated_value, close_date)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (data['client_id'], data['stage'], data['status'], data['notes'], data['estimated_value'], data['close_date'])
            )
            self.conn.commit()

    def update_sales_funnel_entry(self, client_id, data):
        with self.conn.cursor() as cur:
            fields = []
            values = []
            for key, value in data.items():
                fields.append(f"{key} = %s")
                values.append(value)
            
            values.append(client_id)

            cur.execute(
                f"UPDATE sales_funnel SET {', '.join(fields)}, updated_at = %s WHERE client_id = %s;",
                values + [datetime.datetime.now()]
            )
            self.conn.commit()

    def delete_sales_funnel_entry(self, client_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM sales_funnel WHERE client_id = %s;", (client_id,))
            self.conn.commit()

class Client:
    def __init__(self, first_name, last_name, email, phone_number, company=None, position=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.company = company
        self.position = position
        self.notes = ""
        self.last_contact = None
        self.last_contact_source = None
        self.ai_insights = None

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "company": self.company,
            "position": self.position,
            "notes": self.notes,
            "last_contact": self.last_contact.isoformat() if self.last_contact else None,
            "last_contact_source": self.last_contact_source,
            "ai_insights": self.ai_insights,
        }