import os
from zoneinfo import ZoneInfo
import asyncpg
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()


mcp = FastMCP()

DB_URI = os.getenv("DB_URI")


async def transfer_amount(from_acc: int, to_acc: int, amount: float) -> dict:
    """Transfer `amount` from `from_acc` to `to_acc`.

    Returns a dict with success or an error message.
    """
    if amount is None or amount <= 0:
        return {"error": "amount must be a positive number"}

    conn = await asyncpg.connect(DB_URI)
    try:
        async with conn.transaction():
            # Lock both account rows for update to avoid race conditions
            from_row = await conn.fetchrow(
                'SELECT balance FROM public."accounts" WHERE "accNumber" = $1 FOR UPDATE',
                from_acc,
            )
            to_row = await conn.fetchrow(
                'SELECT balance FROM public."accounts" WHERE "accNumber" = $1 FOR UPDATE',
                to_acc,
            )

            if not from_row:
                return {"error": f"from account {from_acc} undefined"}
            if not to_row:
                return {"error": f"to account {to_acc} undefined"}

            from_balance = float(from_row["balance"])
            to_balance = float(to_row["balance"])

            if from_balance < amount:
                return {"error": "insufficient funds"}

            new_from = from_balance - amount
            new_to = to_balance + amount

            await conn.execute(
                'UPDATE public."accounts" SET balance = $1 WHERE "accNumber" = $2',
                new_from,
                from_acc,
            )
            await conn.execute(
                'UPDATE public."accounts" SET balance = $1 WHERE "accNumber" = $2',
                new_to,
                to_acc,
            )

        return {"success": True, "from_acc": from_acc, "to_acc": to_acc, "amount": amount}
    finally:
        await conn.close()


@mcp.tool()
async def guarded_transfer(from_acc: int, to_acc: int, amount: float, approved: bool = False) -> dict:
    """Guarded transfer flow:
    1) Verify `from_acc` is a prime account holder (checks `is_prime` or `account_type=='prime'`).
    2) Verify `from_acc` has sufficient balance.
    3) If not `approved`, return a HITL approval request structure.
    4) If `approved` is True, call `transfer_amount` to perform the transfer.
    """
    if amount is None or amount <= 0:
        return {"error": "amount must be a positive number"}

    conn = await asyncpg.connect(DB_URI)
    try:
        row = await conn.fetchrow(
            'SELECT balance, is_prime FROM public."accounts" WHERE "accNumber" = $1',
            from_acc,
        )
        if not row:
            return {"error": f"from account {from_acc} undefined"}

        # Determine prime status using available columns
        is_prime = False
        try:
            if row.get("is_prime") is not None:
                is_prime = bool(row.get("is_prime"))
            elif row.get("account_type") is not None:
                is_prime = str(row.get("account_type")).lower() == "prime"
        except Exception:
            is_prime = False

        if not is_prime:
            return {"error": "from account is not a prime account holder"}

        from_balance = float(row["balance"])
        if from_balance < amount:
            return {"error": "insufficient funds"}

        # Require human-in-the-loop approval before performing the transfer
        if not approved:
            masked_from = str(from_acc)[-4:]
            masked_to = str(to_acc)[-4:]
            return {
                "requires_approval": True,
                "message": f"Transfer of ${amount:.2f} from account ending {masked_from} to account ending {masked_to} requires human approval.",
                "details": {"from_acc": from_acc, "to_acc": to_acc, "amount": amount},
            }

        # Approved: perform the transfer using existing transfer_amount tool
        result = await transfer_amount(from_acc, to_acc, amount)
        if result.get("error") or result.get("success")== False:
            return {"error": result["error"]}
        return {"success": True, "from_acc": from_acc, "to_acc": to_acc, "amount": amount, "message": "Transfer completed successfully."}
    finally:
        await conn.close()


if __name__ == "__main__":
    mcp.run()
