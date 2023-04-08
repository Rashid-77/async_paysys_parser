from src.logger import get_timed_logger

bin_logger = get_timed_logger('bin', 'parser', 'bin')
bin_logger.info("\nProgram started")


fiat_codes_ = {    
    'Турция':[{'exch_fiat':'TRY', 'region':'', 'banks':[]}], # 'region':'TR'
    'Грузия':[{'exch_fiat':'GEL', 'region':'', 'banks':[]}], # 'region':'GE'
    'Таджикистан':[{'exch_fiat':'USD', 'region':'TJ', 'banks':[]},
                {'exch_fiat':'TJS', 'region':'', 'banks':['DCbank']}],
    'Узбекистан':[{'exch_fiat':'USD', 'region':'UZ', 'banks':['uzcard']},
                {'exch_fiat':'UZS', 'region':'UZ', 'banks':['Humo']}],
    'Киргизия':[{'exch_fiat':'USD', 'region':'KG', 'banks':['BAKAIBANK']}],
    'Казахстан':[{'exch_fiat':'KZT', 'region':'', 'banks':[]}], # KZ
    'Вьетнам':[{'exch_fiat':'USD', 'region':'VN', 'banks':['viettel money', 'zalopay']}],
    'Беларусия':[{'exch_fiat':'BYN', 'region':'', 'banks':[]}], # 'region':'BY'
    'Молдова':[{'exch_fiat':'USD', 'region':'MD', 'banks':['MAIB']}], # 'region':'MD', 'exch_fiat':'MDL'
}


def get_full_code(country:str, fiat:str) -> str:
    try:
        for way in fiat_codes_[country]:
            if fiat == way['exch_fiat']:
                code = way['exch_fiat']
                if fiat == 'USD' or fiat == 'EUR':
                    code += way['region']
                break
    except KeyError as e:
        bin_logger.error(f'KeyError {country}, {fiat} \n{e}')
        return ''
    return code


def get_spread(data:list, pay_name:str, dir:str, fiat:str):
    code = get_full_code(dir, fiat)
    for d in data:
        if pay_name in d[0] and code in d[0].split('-')[2]:
            return d
