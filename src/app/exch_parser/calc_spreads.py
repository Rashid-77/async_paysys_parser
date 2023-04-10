from src.logger import get_timed_logger


logger = get_timed_logger('calc_spr', 'parser', 'calc_spr')

RUB_TO_BE_TRANSFERED = 100000 # just for spread calculation

def try_str_to_float(s:str):
    try: 
        num = float(s)
        return round(num, 5) if num < 0.01 else round(num, 2) 
    except: 
        return s


def calculate_korona_binance_spread(binance_data:list, fiat_transfer_name:list) -> list:

    def is_fiat_usd(description:str)-> bool:
        s = description.split('-')[-1]
        if 'usd' in s.lower():
            return True
        return False
    
    def get_fiat_name(d:str):
        return d[0].split('-')[2]

    logger.info('----')
    spreads =[]
    usdt_rub_rate = try_str_to_float(list(binance_data[-1])[1])
    
    for i in range(len(fiat_transfer_name)):
        f = list(fiat_transfer_name)[i]
        b = list(binance_data)[i]
        logger.debug(f'{f=}')
        if is_fiat_usd(f[0]):
            rate2 = '?'
            spread = calc_spread_without_usd_usdt_conv(
                    RUB_TO_BE_TRANSFERED, f[1], usdt_rub_rate)
        else:
            fiat_name = get_fiat_name(f)
            for j, bd in enumerate(binance_data):
                if fiat_name in bd[0]:
                    b = list(binance_data)[j]
                    break
            logger.debug(f'{b=}')
            rate2 = try_str_to_float(b[1])
            spread = calc_clear_spread(
                    RUB_TO_BE_TRANSFERED, f[1], b[1], usdt_rub_rate)
        li = f[0].split('-')
        logger.debug(f'{li=}')
        pay_name = li[0]
        coin1, coin2, coin3 = li[1], li[2], b[0].split('-')[2]
        rate1 = try_str_to_float(f[1])
        rate3 = try_str_to_float(usdt_rub_rate)
        spr = (f'{pay_name}-{coin1}-{coin2}-{coin3}', \
                rate1, rate2, rate3, spread)
        logger.info(f'{spr}')
        spreads.append(spr)
        s1 = f'{i} {coin1} - {coin2} - {coin3} - {coin1} = {spread}%'
        s2 = f'    {rate1} | {rate2} | {rate3}'
    return spreads


def calc_spread_without_usd_usdt_conv(rub_to_transfer:float, 
                                rub_usd_rate:str, usdt_rub_rate:str) -> float:
    ''' calculate dirty spread, without usd->usdt percents, we can't take it'''
    try:
        usd = rub_to_transfer / float(rub_usd_rate)
        usdt = usd # we dont know real rate beacuse exchange outside of e-exchange
        rub_from_binance = usdt * float(usdt_rub_rate)
        rate = 100 * ((rub_from_binance / rub_to_transfer) - 1)
    except Exception as e:
        rate = 0
    return round(rate, 2)


def calc_clear_spread(rub_to_transfer:float, rub_otherfiat_rate:str, 
                    otherfiat_usdt_rate:str, usdt_rub_rate:str, 
                    ) -> str:
    try:
        otherfiat = rub_to_transfer / float(rub_otherfiat_rate)
        usdt = otherfiat / float(otherfiat_usdt_rate)
        rub_from_binance = usdt * float(usdt_rub_rate)
        rate = 100 * ((rub_from_binance / rub_to_transfer) - 1)
    except Exception as e:
        rate = 0
    return round(rate, 2)


# -----------------------------------------------------------------------------
def calculate_korona_binance_spread_new(binance_data:list, fiat_transfer_name:list) -> list:
    spreads =[]
    usdt_rub = try_str_to_float(list(binance_data[-1])[1])
    c_names =set()
    for country in fiat_transfer_name:
        if country == 'pay_name':
            continue
        c_names.add(country[0].split('-')[1])
    c = {}
    logger.info('----')
    for c_name in c_names:
        ways = []
        rub_other = rub_eur = rub_usd = -3333
        for country in fiat_transfer_name:
            if c_name in country[0] :
                ways.append(country)
                pay_name = country[0].split('-')[0]

        for way in ways:
            if 'USD' in way[0].split('-')[2]:
                rub_usd = way[1]
            elif 'EUR' in way[0].split('-')[2]:
                rub_eur = way[1]
            else:
                rub_other = way[1]

        dirty_spread_usd = calc_spread_without_usd_usdt_conv(
                                                100000.0, 
                                                rub_usd_rate=str(rub_usd), 
                                                usdt_rub_rate=str(usdt_rub))

        dirty_spread_eur = calc_spread_without_usd_usdt_conv(
                                                100000.0, 
                                                rub_usd_rate=str(rub_eur), 
                                                usdt_rub_rate=str(usdt_rub))
        spr = (f'{pay_name}-{c_name}', 
                try_str_to_float(rub_usd), try_str_to_float(rub_eur), 
                try_str_to_float(rub_other), usdt_rub, 
                dirty_spread_usd, dirty_spread_eur
                )
        logger.info(f'{spr}')
        spreads.append(spr)

    return spreads
