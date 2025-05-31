import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()


def init_postgresql():
    db_config = {
        'NAME': os.getenv('POSTGRES_DATABASE'),
        'USER': os.getenv('POSTGRES_USERNAME'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': ''
    }
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            host=db_config['HOST'],
            port=db_config['PORT']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {db_config['NAME']}")
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_config['USER']}') THEN
                    CREATE USER {db_config['USER']} WITH PASSWORD '{db_config['PASSWORD']}';
                END IF;
            END
            $$;
        """)
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_config['NAME']} TO {db_config['USER']}")
        print("Database created successfully")
    except psycopg2.Error as e:
        print(f"Error occure while creating database: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    init_postgresql()
