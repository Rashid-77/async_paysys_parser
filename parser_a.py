
import time
import asyncio
from src.app.exch_parser.spread_storage import SpreadDb
from src.app.exch_parser.binance import get_binance_p2p
from src.app.exch_parser.calc_spreads import calculate_korona_binance_spread_new
from src.app.config.parse_countries import get_country_list
from src.app.exch_parser.korona_pay import parse_korona
from src.app.exch_parser.unistream_pay import parse_unistream

from src.logger import get_logger


logger = get_logger('parser', 'parser', 'parser')
logger.info("\nProgram started")


PARSE_TIME_PERIOD_SEC = 60

db = SpreadDb("spreads")
exchrate_binance = []
exch_bin_rdy = False
exchrate_korona_pay = []
exchrate_unistream_pay = []


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
        logger.info(f'- binance { (end_t - start_t):.3f} sec -')
        
        rest_time = PARSE_TIME_PERIOD_SEC - (end_t - start_t)
        if rest_time <= 0:
            logger.debug(f'- binance longer by {(-rest_time):.1f} s')
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
            logger.debug('"korpay" start parse_korona()')
            await parse_korona(countries, exchrate_korona_pay)

            logger.debug('"korpay"  wait exch_bin_rdy')
            while not exch_bin_rdy:
                await asyncio.sleep(1)
            spreads_new = calculate_korona_binance_spread_new(
                                        exchrate_binance, exchrate_korona_pay)
            logger.debug(f'{spreads_new=}')
            logger.debug('"korpay" calc finished')
            await db.write_spread_v2(spreads_new)
            logger.debug('"korpay" written  spread_v2')

            # for i in await db.read_allspread_v2():
            #     logger.info(f"  {i}")

        except Exception as e:
            logger.error(e)

        end_t = time.time()
        logger.info(f'- korpay { (end_t - start_t):.3f} sec -')
        rest_time = PARSE_TIME_PERIOD_SEC - (end_t - start_t)
        if rest_time <= 0:
            logger.debug(f'- korpay longer by {(-rest_time):.1f} s')
            continue
        if rest_time > PARSE_TIME_PERIOD_SEC:
            rest_time = PARSE_TIME_PERIOD_SEC
        await asyncio.sleep(rest_time)


async def parse_unistr():
    global exch_bin_rdy
    logger.info('--> "parse_unistr()"')
    countries = get_country_list('Unistream')

    while True:
        start_t = time.time()
        try:
            logger.debug('"unistr" start parse_unistr()')
            await parse_unistream(countries, exchrate_unistream_pay)

            logger.debug('"unistr"  wait exch_bin_rdy')
            while not exch_bin_rdy:
                await asyncio.sleep(1)
            spreads_new = calculate_korona_binance_spread_new(
                                    exchrate_binance, exchrate_unistream_pay)
            logger.debug(f'{spreads_new=}')
            logger.debug('"unistr" calc finished')
            await db.write_spread_v2(spreads_new)
            logger.debug('"unistr" written  spread_v2')

            # for i in await db.read_allspread_v2():
            #     logger.info(f"  {i}")

        except Exception as e:
            logger.error(e)

        end_t = time.time()
        logger.info(f'- unistr { (end_t - start_t):.3f} sec -')
        rest_time = PARSE_TIME_PERIOD_SEC - (end_t - start_t)
        if rest_time <= 0:
            logger.debug(f'- unistr longer by {(-rest_time):.1f} s')
            continue
        if rest_time > PARSE_TIME_PERIOD_SEC:
            rest_time = PARSE_TIME_PERIOD_SEC
        await asyncio.sleep(rest_time)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse_bin()), 
        loop.create_task(parse_korpay()), 
        loop.create_task(parse_unistr()), 
    ]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
