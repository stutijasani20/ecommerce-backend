import asyncio
from app.db.database import engine
from sqlalchemy import text

async def check_tables():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        
        for table in tables:
            print(f"\n--- Table: {table} ---")
            print("Columns:")
            result = await conn.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'"))
            for row in result:
                print(row)
            
            print("Constraints:")
            try:
                result = await conn.execute(text(f"SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '{table}'::regclass"))
                for row in result:
                    print(row)
            except Exception as e:
                print(f"Error checking constraints: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
