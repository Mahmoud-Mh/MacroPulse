import psycopg2

try:
    conn = psycopg2.connect(
        dbname='macro_pulse',
        user='postgres',
        password='TAM1234',
        host='localhost',
        port='5432'
    )
    print("Successfully connected to the database!")
    conn.close()
except Exception as e:
    print(f"Error connecting to the database: {e}") 