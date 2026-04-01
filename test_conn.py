import asyncio
import asyncpg
from app.core.config import settings

async def check_conn():
    uri = str(settings.SQLALCHEMY_DATABASE_URI).replace("+asyncpg", "").replace(":postgres@", ":@")
    print(f"Checking connection to: {uri}")
    try:
        conn = await asyncpg.connect(dsn=uri)
        print("Successfully connected!")
        await conn.close()
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(check_conn())
