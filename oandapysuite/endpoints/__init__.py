
from . import accounts
from . import order

prefix = 'https://api-fxtrade.oanda.com'

accounts_for_token = f'{prefix}/v3/accounts'
account_details = lambda accid: f'{accounts_for_token}/{accid}'

def get_candle(ins, gran, count=500, _from=None, to=None):
    if not _from or not to: 
        return f'{prefix}/v3/instruments/{ins}/candles?granularity={gran}&count={count}'
    else: 
        return f'{prefix}/v3/instruments/{ins}/candles?granularity={gran}&from={_from}&to={to}'

def create_order(ins, units):
    request_body = {
        'order': {
            'units': units,
            'instrument': ins,
            'timeInForce': 'FOK',
            'type': 'MARKET',
            'positionFill': "DEFAULT"
        }
    }
    return request_body

close_trade = lambda accid, tradeid: f'{accounts_for_token}/{accid}/trades/{tradeid}/close'