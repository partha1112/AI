import os
from datetime import datetime
import asyncpg
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP()

DB_URI = os.getenv("DB_URI")


@mcp.tool()
async def fetch_transactions( acc_number: int, start_date: str, end_date: str ) -> dict:
    conn = await asyncpg.connect(DB_URI)
    try:
        query = 'SELECT * FROM public."Transactions" WHERE "accNumber" = $1'
        params: list[object] = [acc_number]

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date).date()
            except ValueError:
                return {"error": "start_date must be a valid ISO date string"}
            query += ' AND "date" >= $2'
            params.append(start_dt)

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date).date()
            except ValueError:
                return {"error": "end_date must be a valid ISO date string"}
            if start_date:
                query += ' AND "date" <= $3'
                params.append(end_dt)
            else:
                query += ' AND "date" <= $2'
                params.append(end_dt)

        rows = await conn.fetch(query, *params)
        if not rows:
            return {"transactions": []}
        else:
            return {"transactions": [dict(row) for row in rows]}
    finally:
        await conn.close()


if __name__ == "__main__":
    mcp.run()