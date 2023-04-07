import os
import pymongo
from datetime import datetime
import pytz
from src.logger import get_logger


logger = get_logger('spread_db', 'parser', 'spread_db')
logger.info("\nProgram started")
tz_msc = pytz.timezone('europe/moscow')

MONGO_URI = f'mongodb://{os.getenv("MONGO_DB", "")}'

class SpreadDb():
    client = pymongo.MongoClient(MONGO_URI)
    
    def __init__(self, db_name: str):
        if self.client is None:
            logger.error("No conection to db")
            return
        self.db = self.client[db_name]
        db_info = self.db["db_info"]
        self.spr1 = self.db["spread_v1"]
        self.spr2 = self.db["spread_v2"]
        if db_name not in self.client.list_database_names():
            db_info.insert_one({'created': datetime.utcnow()})


    async def read_spread_v1(self, name):
        return self.spr1.find_one({'name':name})


    async def write_spread_v1(self, name, rub_val_rate, val_usdt_rate, 
                                usdt_rub_rate, spread):
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        spr = self.spr1.find_one({'name':name})
        logger.debug(f'{spr=}')
        data = {
            'name': name,
            'rub_val_rate': rub_val_rate,
            'val_usdt_rate': val_usdt_rate,
            'usdt_rub_rate': usdt_rub_rate,
            'spread': spread,
            'date': now_msc,
        }
        if spr is None:
            res = self.spr1.insert_one(data)
        else:
            res = self.spr1.update_one({'name':name}, 
                                       {'$set': {
                                                'name': name,
                                                'rub_val_rate': rub_val_rate,
                                                'val_usdt_rate': val_usdt_rate,
                                                'usdt_rub_rate': usdt_rub_rate,
                                                'spread': spread,
                                                'date': now_msc,
                                                }
                                        })
            logger.debug(f'upd {res=}')


    async def read_spread_v2(self):
        pass


    async def write_spread_v2(self):
        pass
