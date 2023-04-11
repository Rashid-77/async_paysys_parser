import json
import httpx
from httpx import Timeout
from src.logger import get_timed_logger


logger = get_timed_logger('req_err', 'parser', 'req_err')
logger.info("\nProgram started")

REQ_TIMEOUT = 30


async def request_get(url, headers=None):
    async with httpx.AsyncClient(timeout=Timeout(REQ_TIMEOUT)) as client:
        response = await client.get(url, headers=headers, 
                                        follow_redirects=True)
    return response


async def request_get_json(url, headers=None, logger=None):
    async with httpx.AsyncClient(timeout=Timeout(REQ_TIMEOUT)) as client:
        response = await client.get(url, headers=headers,
                                        follow_redirects=True)
    return process_err(url, response)


async def request_post_json(url, json_post, headers=None):
    async with httpx.AsyncClient(timeout=Timeout(REQ_TIMEOUT)) as client:
        response = await client.post(url, json=json_post, headers=headers, 
                                                    follow_redirects=True)
    return process_err(url, response)


def process_err(url, response):
    if response.status_code != 200:
        logger.error(f'{url} - {response.status_code}')
        return None

    if 'content-type' not in response.headers:
        logger.error('content-type header not found')
        return None

    if 'application/json' not in response.headers['content-type']:
        logger.error(f'content-type : {response.headers["content-type"]}')
        return None

    try:
        data = json.loads(response.text)
    except Exception as e:
        data = None
        logger.exception(e)
    
    return data