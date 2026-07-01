import json

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
        return [dict(row) for row in rows]


    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return []

def load_instinct_patterns(host='localhost', port=5434, dbname='postgres', user='postgres', password='Postgres'):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT pattern, actions FROM agi_prototype.instinct_patterns")

        rows = cur.fetchall()
        cur.close()
        conn.close()
        patterns = []
        for row in rows:
            pattern = row['pattern'] if isinstance(row['pattern'], dict) else json.loads(row['pattern'])
            action = row['actions'] if isinstance(row['actions'], dict) else json.loads(row['actions'])
            patterns.append({'pattern': pattern, 'action': action})
        return patterns


    except Exception as e:
        print(f"Ошибка подключения к БД (инстинкты): {e}")
        return []