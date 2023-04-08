
import time
import asyncio
from src.app.exch_parser.spread_storage import SpreadDb
from src.app.exch_parser.binance import get_binance_p2p
from src.app.exch_parser.calc_spreads import calculate_korona_binance_spread_new
from src.app.config.parse_countries import get_country_list
from src.app.exch_parser.korona_pay import parse_korona

from src.logger import get_logger


logger = get_logger('parser', 'parser', 'parser')
logger.info("\nProgram started")


PARSE_TIME_PERIOD_SEC = 60

db = SpreadDb("spreads")
exchrate_binance = []
exch_bin_rdy = False
exchrate_korona_pay = []


async def parse_bin():
    global exch_bin_rdy
    logger.info('--> "parse_bin()"')
    while True:
        start_t = time.time()
        exchrate_binance.clear()
        exch_bin_rdy = False

        try:
            await get_binance_p2p(exchrate_binance)
            for i in exchrate_binance:
                if i[0] == 'bin-USDT-RUB':
                    logger.debug(f'{i=}')
                    await db.write_usdt_rub(i[0], i[1])
                    exch_bin_rdy = True
                    break
        except Exception as e:
            logger.error(e)

        end_t = time.time()
        # logger.info(f'- All queries in { (end_t - start_t):.3f} sec -\n')
        
        rest_time = PARSE_TIME_PERIOD_SEC - (end_t - start_t)
        if rest_time <= 0:
            logger.debug(f'-- longer by {(-rest_time):.1f} s')
            continue
        if rest_time > PARSE_TIME_PERIOD_SEC:
            rest_time = PARSE_TIME_PERIOD_SEC
        await asyncio.sleep(rest_time)


async def parse_korpay():
    global exch_bin_rdy
    logger.info('--> "parse_korpay()"')
    countries = get_country_list('KoronaPay')

    while True:
        start_t = time.time()
        try:
            logger.debug('parse_korpay()  wait "exch_bin_rdy"')
            while not exch_bin_rdy:
                await asyncio.sleep(1)
            logger.debug('start parse_korona()')
            await parse_korona(countries, exchrate_korona_pay)
            spreads_new = calculate_korona_binance_spread_new(
                                        exchrate_binance, exchrate_korona_pay)
            logger.debug('calc finished')
            await db.write_spread_v2(spreads_new)
            logger.debug('written  spread_v2')

        except Exception as e:
            logger.error(e)

        end_t = time.time()
        # logger.info(f'- All queries in { (end_t - start_t):.3f} sec -\n')
        rest_time = PARSE_TIME_PERIOD_SEC - (end_t - start_t)
        if rest_time <= 0:
            logger.debug(f'-- longer by {(-rest_time):.1f} s')
            continue
        if rest_time > PARSE_TIME_PERIOD_SEC:
            rest_time = PARSE_TIME_PERIOD_SEC
        await asyncio.sleep(rest_time)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse_bin()), 
        loop.create_task(parse_korpay()), 
    ]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
