import asyncio
import os
from src.app.exch_parser.req_check_err_a import request_get_json
from src.app.exch_parser.country_fiat_info import fiat_info

from src.logger import get_logger

logger = get_logger('unistr', 'parser', 'unistr')
logger.info("\nProgram started")

TOKEN_PATH = '/code/src/app/exch_parser/unistr_token.txt'

unistream_dirs = {
    'pay_name':'Unistream',
    'Турция':[{'country_code':'TUR', 'currency':'TRY','amount':30000}],
    'Узбекистан':[  
                    {'country_code':'UZB', 'currency':'USD', 'amount':800},
                    {'country_code':'UZB', 'currency':'EUR', 'amount':800},
                    {'country_code':'UZB', 'currency':'UZS', 'amount':800000},
                ],
}


async def get_unistream_exch_rates(country_name:str, alter_way:dict, token:str) -> tuple:
    country_code = alter_way['country_code']
    currency = alter_way['currency']
    amount = alter_way['amount']
    url = f'https://online.unistream.ru/api/card2cash/calculate?' \
            f'destination={country_code}&amount={amount}&currency={currency}&' \
            f'accepted_currency=RUB&profile=unistream_front'

    header = {
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) "\
                        "Gecko/20100101 Firefox/108.0",
        "authorization": token
    }    

    json_d = await request_get_json(url, header)
    
    fiat = currency
    if fiat == 'USD' or fiat == 'EUR':
        fiat += fiat_info.get_country_region_code(country_name)

    pay_name = unistream_dirs['pay_name']
    if json_d is None:
        d = (f'{pay_name}-{country_name}-RUB-{fiat}', 'proto_err', 0, 0, 0)
        logger.error('json is None (protocol error)')
        clear_token()
        return d
    
    try:
        sendingAmount = json_d['fees'][0]['acceptedAmount']
        withdrawAmount = json_d['fees'][0]['withdrawAmount']
        acceptedTotalFee = json_d['fees'][0]['acceptedTotalFee']
        exch_rate = sendingAmount / withdrawAmount
        exch_rate = round(exch_rate, 5) if fiat == 'UZS' else  round(exch_rate, 2)
        d = (f'{pay_name}-{country_name}-{fiat}', str(exch_rate), str(acceptedTotalFee), 0, 0)
    except Exception as e:
        logger.error(e)
        d = (f'{pay_name}-{country_name}-{fiat}', 'no_price', 0, 0, 0)
        clear_token()
    return d


async def parse_unistream(countries:tuple, data_list:list):
    token = check_token()
    logger.info('----')
    if token == '':
        logger.info('token not exist - wait for token')
        return

    for country in countries:
        for way in unistream_dirs[country]:
            d = await get_unistream_exch_rates(country, way, token)
            data_list.append(d)
            logger.info(d)
            await asyncio.sleep(1)


def check_token() -> str:
    token = ''
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as f:
            token = f.read()
    return token


def clear_token():
    with open(TOKEN_PATH, 'w') as f:
        token = f.write('None')
