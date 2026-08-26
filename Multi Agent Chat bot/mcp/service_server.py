import os
import sys
import asyncpg
import logging
from mcp.server.fastmcp import Context, FastMCP
from dotenv import load_dotenv

# Ensure project root is on sys.path so top-level package imports like
# `backend` work when this script is executed from the `mcp/` directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

mcp = FastMCP()

DB_URI = os.getenv("DB_URI")


@mcp.tool()
async def service_update(acc_number: int, email: str, address: str, ctx: Context) -> dict:
    email_unmasked = email
    conn = await asyncpg.connect(DB_URI)
    try:
        updates = []
        params = []

        if email_unmasked not in (None, ""):
            updates.append(f"email = ${len(params) + 1}")
            params.append(email_unmasked)

        if address not in (None, ""):
            updates.append(f"address = ${len(params) + 1}")
            params.append(address)

        query = (
            'UPDATE public."accountsinformation" '
            f"SET {', '.join(updates)} "
            f"WHERE \"accNumber\" = ${len(params) + 1}"
        )
        params.append(acc_number)

        await conn.execute(query, *params)
        return {"success": True, "updated_fields": updates}
    finally:
        await conn.close()


if __name__ == "__main__":
    mcp.run()