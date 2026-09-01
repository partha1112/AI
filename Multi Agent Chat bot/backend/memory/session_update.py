from datetime import datetime
from backend.memory.Session import Session
import psycopg
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

DB_URI = os.getenv("DB_URI")

def create_session(session: Session):
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public."Session"(session_id, "accNumber", status, created_at, last_activity)
                VALUES (%s, %s, %s, %s, %s) """,
                (session.session_id, session.account_id, session.status, session.crearted_at, session.last_activity)
            )
            conn.commit()
            print("Session saved successfully")

def get_session(session_id: str) -> Session:
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM public."Session" WHERE session_id = %s and status = 'ACTIVE'
            """, (session_id,))
            res = cur.fetchone()
            if res:
                return Session(session_id=res[0], account_id=res[1], status=res[2], crearted_at=res[3], last_activity=res[4])
            return None

def update_session(status :str, last_activity: datetime, session_id: str):
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE public."Session" SET status = %s, last_activity = %s WHERE session_id = %s
            """, (status, last_activity, session_id))
            conn.commit()
            print("Session updated successfully")
