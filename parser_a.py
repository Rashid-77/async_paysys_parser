
import asyncio
from src.app.exch_parser.spread_storage import SpreadDb

from src.logger import get_logger


logger = get_logger('parser', 'parser', 'parser')
logger.info("\nProgram started")




async def parser():
    db = SpreadDb("spreads")
    await db.write_spread_v1('abc', 1,1,1,1)
    await db.write_spread_v1('xyz', 5,5,5,5)
    while True:
        await asyncio.sleep(30)
        logger.info('...')
        


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser())
    