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
        self.usdt_rub = self.db["usdt_rub"]
        self.spr1 = self.db["spread_v1"]
        self.spr2 = self.db["spread_v2"]
        if db_name not in self.client.list_database_names():
            db_info.insert_one({'created': datetime.utcnow()})


    async def read_spread_v1(self, name):
        spr = self.spr1.find_one({'_id':name})
        if spr is None:
            return tuple(name, 'not_rdy', 'not_rdy', 
                         'not_rdy', 'not_rdy', 'not_rdy')
            # return tuple(name, 0, 0, 0, 0, 0) 
        return tuple(spr['data'])


    async def write_spread_v1(self, name, rub_val_rate, val_usdt_rate, 
                                usdt_rub_rate, spread):
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        spr = self.spr1.find_one({'_id':name})
        logger.debug(f'spr1={spr}')
        if spr is None:
            self.spr1.insert_one({'_id': name,
                                'data':(name,
                                        rub_val_rate,
                                        val_usdt_rate,
                                        usdt_rub_rate,
                                        spread,
                                        now_msc,)
                                })
        else:
            self.spr1.update_one({'_id':name}, 
                               {'$set': {
                                        'data':(name,
                                                rub_val_rate,
                                                val_usdt_rate,
                                                usdt_rub_rate,
                                                spread,
                                                now_msc,)
                                        }
                                })


    async def read_spread_v2(self, name):
        spr = self.spr2.find_one({'_id':name})
        if spr is None:
            return tuple(name, 'not_rdy', 'not_rdy', 'not_rdy', 
                         'not_rdy', 'not_rdy', 'not_rdy', 'not_rdy')
            # return tuple(name, 0, 0, 0, 0, 0, 0, 0)
        return tuple(spr['data'])


    async def write_spread_v2(self, name, rub_usd, rub_eur, rub_other,
                                usdt_rub, dirty_spread_usd, dirty_spread_eur):
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        spr = self.spr2.find_one({'_id':name})
        logger.debug(f'spr2={spr}')
        if spr is None:
            self.spr2.insert_one({'_id': name,
                                'data':(name,
                                        rub_usd,
                                        rub_eur,
                                        rub_other,
                                        usdt_rub,
                                        dirty_spread_usd,
                                        dirty_spread_eur,
                                        now_msc,)
                                })
        else:
            self.spr2.update_one({'_id':name}, 
                               {'$set': {
                                        'data':(name,
                                                rub_usd,
                                                rub_eur,
                                                rub_other,
                                                usdt_rub,
                                                dirty_spread_usd,
                                                dirty_spread_eur,
                                                now_msc,)
                                        }
                                })


    async def write_usdt_rub(self, name, usdt_rub):
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        spr = self.usdt_rub.find_one({'_id':name})
        logger.debug(f'usdt_rub={spr}')
        if spr is None:
            self.usdt_rub.insert_one({'_id': name,
                                    'data':(name,
                                            usdt_rub,)
                                })
        else:
            self.usdt_rub.update_one({'_id':name}, 
                                    {'$set': {
                                            'data':(name,
                                                    usdt_rub,)
                                            }
                                    })

    
    async def read_usdt_rub(self, name):
        cur = self.usdt_rub.find_one({'_id':name})
        if cur is None:
            return tuple(name, 'not_rdy')
            # return tuple(name, 0, 0, 0, 0, 0, 0, 0)
        return tuple(cur['data'])
