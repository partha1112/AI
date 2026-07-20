import asyncio
from weather import get_weather_resort

async def main() -> None:
    res = await get_weather_resort("NY")
    print(f"test resp :{res}")

if __name__ == "__main__":
    asyncio.run(main())
