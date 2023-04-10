import os
import time
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


    async def read_allspread_v1(self):
        ret = [tuple(i['data']) for i in self.spr1.find({})]
        # logger.debug(f'{type(ret)=}')
        return ret


    async def read_spread_v1(self, name):
        spr = self.spr1.find_one({'_id':name})
        if spr is None:
            return tuple(name, 'not_rdy', 'not_rdy', 
                         'not_rdy', 'not_rdy', 'not_rdy')
        return tuple(spr['data'])


    async def write_spread_v1(self, data: list):
        start_t = time.time()
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        for i in data:
            d = (i[0], i[1], i[2], i[3], i[4], now_msc,)
            name = i[0]
            spr = self.spr1.find_one({'_id':name})
            if spr is None:
                self.spr1.insert_one({'_id': name, 'data': d})
            else:
                self.spr1.update_one({'_id':name}, {'$set': { 'data': d}})
        end_t = time.time()
        logger.info(f'wr_spr2 { (end_t - start_t):.3f} sec -')

            # spr = self.spr1.find_one({'_id':name})
            # logger.debug(f'spr1={spr}')
            # if spr is None:
            #     self.spr1.insert_one({'_id': name,
            #                         'data':(name,
            #                                 rub_val_rate,
            #                                 val_usdt_rate,
            #                                 usdt_rub_rate,
            #                                 spread,
            #                                 now_msc,)
            #                         })
            # else:
            #     self.spr1.update_one({'_id':name}, 
            #                     {'$set': {
            #                                 'data':(name,
            #                                         rub_val_rate,
            #                                         val_usdt_rate,
            #                                         usdt_rub_rate,
            #                                         spread,
            #                                         now_msc,)
            #                                 }
            #                         })


    async def read_allspread_v2(self):
        ret = [tuple(i['data']) for i in self.spr2.find({})]
        # logger.debug(f'{type(ret)=}')
        return ret


    async def read_spread_v2(self, name):
        spr = self.spr2.find_one({'_id':name})
        if spr is None:
            return tuple(name, 'not_rdy', 'not_rdy', 'not_rdy', 
                         'not_rdy', 'not_rdy', 'not_rdy', 'not_rdy')
            # return tuple(name, 0, 0, 0, 0, 0, 0, 0)
        return tuple(spr['data'])


    async def write_spread_v2(self, data: list):
        start_t = time.time()
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        for i in data:
            d = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], now_msc,)
            name = i[0]
            spr = self.spr2.find_one({'_id':name})
            if spr is None:
                self.spr2.insert_one({'_id': name, 'data': d})
            else:
                self.spr2.update_one({'_id':name}, {'$set': { 'data': d}})
        end_t = time.time()
        logger.info(f'wr_spr2 { (end_t - start_t):.3f} sec -')


    async def write_usdt_rub(self, name, usdt_rub):
        now_msc = datetime.now(tz_msc)
        now_msc = now_msc.strftime('%Y:%m:%d %H:%M %Z')
        spr = self.usdt_rub.find_one({'_id':name})
        d = (name, usdt_rub, now_msc,)
        if spr is None:
            self.usdt_rub.insert_one({'_id': name, 'data':d})
        else:
            self.usdt_rub.update_one({'_id':name}, {'$set': {'data': d}})

    
    async def read_usdt_rub(self, name):
        cur = self.usdt_rub.find_one({'_id':name})
        if cur is None:
            return tuple(name, 'not_rdy', 0)
        return tuple(cur['data'])
