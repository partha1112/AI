import os
import asyncpg
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()


mcp = FastMCP()

DB_URI = os.getenv("DB_URI")

@mcp.tool()
async def fetch_account_details() -> dict:
    acc_number = os.getenv("CUSTOMER_ACCOUNT_NUMBER")
    if not acc_number:
        return {"error": "Account number is not available"}
    conn = await asyncpg.connect(DB_URI)
    try:
        row = await conn.fetchrow(f"""
            select "accNumber", balance from public."accounts"
            where "accNumber"={acc_number}
            """
        )
        if row:
            return dict(row)

        return {"error" : "Account undefined"}
    finally:
        await conn.close()

if __name__ == "__main__":
    mcp.run()