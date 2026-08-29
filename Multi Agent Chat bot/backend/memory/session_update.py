from backend.memory.session import Session
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI")

def update_session(session: Session):
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.session(service, context, session_id, account_id)
                VALUES (%s, %s, %s, %s) """,
                (session.service, session.context, session.session_id, session.account_id)
            )
            conn.commit()
            print("Session saved successfully")

def get_session(session_id: str) -> Session:
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT context FROM public.session WHERE session_id = %s
            """, (session_id,))
            return cur.fetchall()
