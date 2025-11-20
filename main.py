import asyncio
from src.CerbyToken import CerbyTokenRetriever


if __name__ == "__main__":
    asyncio.run(CerbyTokenRetriever().run())