import asyncio
import traceback
from inspect import currentframe, getframeinfo
from src.app.exch_parser.req_check_err_a import request_post_json
from src.app.exch_parser.binance_stuff import fiat_codes_, bin_logger


async def request_binance_p2p(coin='USDT', trade_type='BUY', 
                              pay_type=['TinkoffNew'], countries='', 
                              page_size=3, trans_amount=0, 
                              fiat='RUB') -> list:
    """
    :param coin: Валюта
    :param trade_type: Покупка/Продажа
    :param pay_type: Банки
    :param page_size: Max размер вывода продавцов/покупателей
    :param trans_amount: Сумма, которую клиент расчитывает потратить
    :param fiat: Валюта покупки
    :return: Кортеж с данными p2p вида ('QIWI-BUY-BNB-MAX', '18639.78', 0, 0, 0)
    """
    _data = ()
    if trade_type == 'SELL':
        _name = f'bin-{fiat}{countries}-{coin}'
    else:
        _name = f'bin-{coin}-{fiat}{countries}'
    # _name = pay_type + '-' + trade_type + '-' + fiat + '->' + coin + '-' + trans_amount[1]

    p = [] if pay_type == '' else pay_type
    c = [] if countries == '' else [countries]
    json_data = {
        'page': 1,
        'rows': page_size,
        'payTypes': p,
        'countries': c,
        'publisherType': None,
        'transAmount': trans_amount[0],
        'asset': coin,
        'fiat': fiat,
        'tradeType': trade_type,
    }
    try:
        json_d = await request_post_json('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', json_post=json_data)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        bin_logger.error(f'{traceback.format_exc()} {frameinfo.filename} {frameinfo.lineno} \n{e}')
        _data = (_name, "error from binance", 'NO', 'NO', 'NO')

    if json_d is None or len(json_d['data']) == 0:
        _data = (_name, "no offers", 'NO', 'NO', 'NO')
    else:
        try:
            if fiat == 'UZS':
                adverts = len(json_d['data'])
                if adverts > 3:
                    adverts = 3
                sum = 0
                for n in range(adverts):
                    # i = json_d['data'][n]['adv']
                    # _price = i['price']
                    sum += float(json_d['data'][n]['adv']['price'])
                _price = str(round(sum/3, 2))
            else:
                i = json_d['data'][0]['adv']
                _price = i['price']

            # _available = i['surplusAmount']
            # _min_amount = i['minSingleTransAmount']
            # _max_amount = i['maxSingleTransAmount']
            # _data = (_name, _price, _available, _min_amount, _max_amount)
            _data = (_name, _price, 0,0,0)
        except Exception as e:
            frameinfo = getframeinfo(currentframe())
            bin_logger.error(f'{traceback.format_exc()} {frameinfo.filename} {frameinfo.lineno} \n{e}')
            _data = (_name, "no offers", 'NO', 'NO', 'NO')

    return _data


async def get_binance_p2p(data_list:list):

    bin_logger.info('----')
    for country in fiat_codes_:
        for way in fiat_codes_[country]:
            fiat = way['exch_fiat']
            banks = way['banks']# if fiat == 'USD' else ''
            countries = way['region'] if fiat == 'USD' else ''
            d = await request_binance_p2p(coin='USDT', trade_type='SELL', pay_type=banks, 
                                countries=countries, trans_amount=[0, '0'], fiat=fiat)
            data_list.append(d)
            bin_logger.info(d)
            await asyncio.sleep(2)
            
    d = await request_binance_p2p(coin='USDT', pay_type=['TinkoffNew'], trade_type='BUY', 
                                        trans_amount=[50000, '50000'], fiat='RUB')
    data_list.append(d)
    bin_logger.info(d)

    return data_list


#------------------------------------------------------------------------------

# def init_data(d, fiats):
#     for coin in fiats:
#         d[coin] = 'outdated'

