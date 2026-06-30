import psycopg2
import psycopg2.extras

def load_reflex_rules(host='localhost', port=5434, dbname='postgres', user='postgres', password='Postgres'):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT sense_type, signal_type, signal_threshold, action FROM agi_prototype.reflex_pattern")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        print(dict(row) for row in rows) # контрольный лог

        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return []
