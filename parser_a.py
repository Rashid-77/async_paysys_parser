
import time
import asyncio
from src.app.exch_parser.spread_storage import SpreadDb
from src.app.exch_parser.binance import get_binance_p2p

from src.logger import get_logger


logger = get_logger('parser', 'parser', 'parser')
logger.info("\nProgram started")


PARSE_TIME_PERIOD_SEC = 60


async def parser():
    db = SpreadDb("spreads")

    while True:
        start_t = time.time()
        exchrate_binance = []


        try:
            await get_binance_p2p(exchrate_binance)
            for i in exchrate_binance:
                if i[0] == 'bin-USDT-RUB':
                    logger.debug(f'{i=}')
                    await db.write_usdt_rub(i[0], i[1])
                    break


        except Exception as e:
            logger.error(e)

        end_t = time.time()
        logger.info(f'- All queries in { (end_t - start_t):.3f} sec -\n')
        rest_time = PARSE_TIME_PERIOD_SEC - (end_t - start_t)
        if rest_time <= 0:
            logger.debug(f'-- longer by {(-rest_time):.1f} s')
            continue
        if rest_time > 60:
            rest_time = 60
        time.sleep(rest_time)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser())
    