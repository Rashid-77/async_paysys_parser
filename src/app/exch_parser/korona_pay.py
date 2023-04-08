import time
from src.app.exch_parser.req_check_err_a import request_get_json
from src.app.exch_parser.country_fiat_info import fiat_info

import traceback
from inspect import currentframe, getframeinfo
from src.logger import get_timed_logger

korpay_logger = get_timed_logger('korpay', 'parser', 'korpay')
korpay_logger.info("\nProgram started")


# data for interacting with KoronaPay
korona_dirs = {
    'pay_name':'KoronaPay',
    'Турция':[{'country_code':'TUR', 'exch_rate':0, 'recv_cur':'TRY', 'paidNotif':'true', 'receivAmount':100},
                {'country_code':'TUR', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':100},
                {'country_code':'TUR', 'exch_rate':0, 'recv_cur':'EUR', 'paidNotif':'true', 'receivAmount':100},],
    'Грузия':[{'country_code':'GEO', 'exch_rate':0, 'recv_cur':'GEL', 'paidNotif':'true', 'receivAmount':100},
                {'country_code':'GEO', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':100},
                {'country_code':'GEO', 'exch_rate':0, 'recv_cur':'EUR', 'paidNotif':'true', 'receivAmount':100},],
    'Таджикистан':[{'country_code':'TJK', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'false', 'receivAmount':10000}],
    'Узбекистан':[{'country_code':'UZB', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':10000}],
    'Киргизия':[{'country_code':'KGZ', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':100}],
    'Казахстан':[{'country_code':'KAZ', 'exch_rate':0, 'recv_cur':'KZT', 'paidNotif':'true', 'receivAmount':71000000},
                {'country_code':'KAZ', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':100},],
    'Вьетнам':[{'country_code':'VNM', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':10000}],
    # 'Беларусия':{'country_code':'BLR', 'exch_rate':0, 'recv_cur':'RUB', 'paidNotif':'true', 'receivAmount':5000000},
    'Молдова':[{'country_code':'MDA', 'exch_rate':0, 'recv_cur':'USD', 'paidNotif':'true', 'receivAmount':1000},
                {'country_code':'MDA', 'exch_rate':0, 'recv_cur':'EUR', 'paidNotif':'true', 'receivAmount':1000},]
}


async def get_korona_exch_rates(country_name:str, alter_way:dict) -> tuple:
    country_code = alter_way['country_code']
    paidNotif = alter_way['paidNotif']
    recv_cur_id = fiat_info.get_iso4217(alter_way['recv_cur'])   #fiat_names[alter_way['recv_cur']]['iso_4217']
    rec_amount = alter_way['receivAmount']
    url = f'https://koronapay.com/transfers/online/api/transfers/tariffs?' \
            f'sendingCountryId=RUS&sendingCurrencyId=810&receivingCountryId={country_code}' \
            f'&receivingCurrencyId={recv_cur_id}&paymentMethod=debitCard&receivingAmount={rec_amount}' \
            f'&receivingMethod=cash&paidNotificationEnabled={paidNotif}'
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}    
    
    json_d = await request_get_json(url, header)

    fiat = alter_way['recv_cur']
    if fiat == 'USD' or fiat == 'EUR':
        fiat += fiat_info.get_country_region_code(country_name)


    pay_name = korona_dirs['pay_name']
    if json_d is None:
        d = (f'{pay_name}-RUB-'+fiat, 'proto_err', 0, 0, 0)
        korpay_logger.error('json is None (protocol error)')
        return d
    try:
        exch_rate = '1' if recv_cur_id == 810 else json_d[0]['exchangeRate']
        try:
            sendingAmount = json_d[0]['sendingAmount']
            transf_commiss = json_d[0]['sendingTransferCommission']
            transf_commis_perc = (transf_commiss / sendingAmount) * 100
            transf_commis_perc = round(transf_commis_perc, 2)
        except KeyError:
            transf_commiss = 0
        # d = (f'{pay_name}-RUB-'+fiat, str(exch_rate), str(transf_commis_perc), 0, 0)
        d = (f'{pay_name}-{country_name}-{fiat}', str(exch_rate), str(transf_commis_perc), 0, 0)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        korpay_logger.error(f'{traceback.format_exc()} {frameinfo.filename} {frameinfo.lineno} \n{e}')
        d = (f'{pay_name}-{country_name}-{fiat}', 'no_price', 0, 0, 0)
        # d = (f'{pay_name}-RUB-'+fiat, 'no_price', 0, 0, 0)
    
    return d
        

async def parse_korona(countries:tuple, data_list:list) -> list:
    korpay_logger.info('----')
    for country_name in countries:
        for way in korona_dirs[country_name]:        
            d = await get_korona_exch_rates(country_name, way)
            korpay_logger.info(d)
            data_list.append(d)
            time.sleep(4)
