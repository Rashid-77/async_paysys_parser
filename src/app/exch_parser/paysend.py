from bs4 import BeautifulSoup as Bs
from src.app.exch_parser.req_check_err_a import request_get, request_get_json
from src.logger import get_timed_logger

logger = get_timed_logger('paysend', 'parser', 'paysnd')
logger.info("\nProgram started")

paysend_dirs = {
    'pay_name':'Paysend',
    'Узбекистан':[{'country_code':'UZB', 'currency':'UZS',
                'url':'https://paysett.ru/ru-ru/otpravit-dengi/iz-rossii-v-uzbekistan?'\
                'fromCurrId=643&toCurrId=860&isFrom=true', 
                'amount':51000 },
                ],
}


async def get_paysend_exch_rates(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    
    response = await request_get(url, headers=header)
    if response.status_code != 200:
        logger.error(f'response={response.status_code}')
        return None
    
    soup = Bs(response.text, 'html.parser')
    section = Bs(str(soup), 'html.parser')
    rate_content = section.find('span', class_='foo')

    temp  = rate_content.contents[0]
    temp = str(temp).split('=')[1]
    temp = temp.split()
    
    if temp[1] == 'UZS':
        exch_rate = 1 / float(temp[0])
    else:
        logger.error(f'exchrate not parsed {temp[1]}')
        exch_rate = 'not parsed'
    
    fee_content = section.find('div', class_='fee-table-row fee-table-row_first')

    for i in fee_content:
        if 'RUB' in i.text:
            fee_val = str(i.text)
            fee_val = fee_val.split()[0]
            
    return (f'Paysend-RUB-UZS', str(exch_rate), str(fee_val), 0, 0)


async def parse_paysend(countries:str, data_list:list):

    logger.info('----')
    for country in paysend_dirs:
        if country == 'pay_name':
            continue
        for way in paysend_dirs[country]:
            d = await get_paysend_exch_rates(way['url'])
            data_list.append(d)
            logger.info(d)

    return data_list
