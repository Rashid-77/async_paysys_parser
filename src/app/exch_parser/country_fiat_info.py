from inspect import currentframe, getframeinfo
from src.logger import get_logger


logger = get_logger(__name__, 'parser', 'cntryfiat')
logger.info("\nProgram started")


class Fiat_info():
    fiat_names = {
        'TRY':{'iso_4217':949, 'name':'лира'},
        'GEL':{'iso_4217':981, 'name':'груз.лари'},
        'TJS':{'iso_4217':972, 'name':'тадж.сомони'},
        'USD':{'iso_4217':840, 'name':'доллар'},
        'KZT':{'iso_4217':398, 'name':'казах.тенге'},
        'RUB':{'iso_4217':810, 'name':'рубль'},
        'BYN':{'iso_4217':810, 'name':'рубль'},
        'MDL':{'iso_4217':498, 'name':'молд.лей'},
        'EUR':{'iso_4217':978, 'name':'евро'}
    }

    local_currency = {
        'россия':{'code':'RUB', 'name':'рубль', 'reg':'RU', 'flag':'🇷🇺'}, 
        'турция': {'code':'TYR', 'name':'лира', 'reg':'TR', 'flag':'🇹🇷'},
        'грузия': {'code':'GEL', 'name':'груз.лари', 'reg':'GE', 'flag':'🇬🇪'},
        'таджикистан': {'code':'TJS', 'name':'тадж.сомони', 'reg':'TJ', 'flag':'🇹🇯'},
        'узбекистан': {'code':'UZS', 'name':'узбек.сум', 'reg':'UZ', 'flag':'🇺🇿'},
        'киргизия': {'code':'KGS', 'name':'кирг.сом', 'reg':'KG', 'flag':'🇰🇬'},
        'казахстан': {'code':'KZT', 'name':'казах.тенге', 'reg':'KZ', 'flag':'🇰🇿'},
        'вьетнам': {'code':'VND', 'name':'вьетн.донг', 'reg':'VN', 'flag':'🇻🇳'},
        'беларусия': {'code':'BYN', 'name':',белор.рубль', 'reg':'BY', 'flag':'🇧🇾'},
        'молдова': {'code':'MDL', 'name':'молд.лей', 'reg':'MD', 'flag':'🇲🇩'},
    }

    def get_iso4217(self, fiat:str) -> int:
        try:
            return self.fiat_names[fiat]['iso_4217']
        except KeyError:
            frameinfo = getframeinfo(currentframe())
            logger.info(f'bad fiat  - {fiat}. Use TRY, USD, BYN ...)\n \
                        {frameinfo.filename} {frameinfo.lineno}')

    def get_name(self, fiat:str) -> str:
        try:
            return self.fiat_names[fiat]['name']
        except KeyError:
            frameinfo = getframeinfo(currentframe())
            logger.info(f'bad fiat  - {fiat}. Use TRY, USD, BYN ...)\n \
                        {frameinfo.filename} {frameinfo.lineno}')

    def get_local_currency_abc_code(self, country_name:str) -> str:
        try:
            return self.local_currency[country_name.lower()]['name']
        except KeyError:
            frameinfo = getframeinfo(currentframe())
            logger.info(f'bad country name - {country_name}\n \
                        {frameinfo.filename} {frameinfo.lineno}')

    def get_local_currency_name(self, country_name:str) -> str:
        try:
            return self.local_currency[country_name.lower()]['name']
        except KeyError:
            frameinfo = getframeinfo(currentframe())
            logger.info(f'bad country name - {country_name}\n \
                        {frameinfo.filename} {frameinfo.lineno}')

    def get_country_region_code(self, country_name:str) -> str:
        try:
            return self.local_currency[country_name.lower()]['reg']
        except KeyError:
            frameinfo = getframeinfo(currentframe())
            logger.info(f'bad country name - {country_name}\n \
                        {frameinfo.filename} {frameinfo.lineno}')

    def get_country_flag(self, country_name:str) -> str:
        try:
            return self.local_currency[country_name.lower()]['flag']
        except KeyError:
            frameinfo = getframeinfo(currentframe())
            logger.info(f'bad country name - {country_name}\n \
                        {frameinfo.filename} {frameinfo.lineno}')

fiat_info = Fiat_info()
