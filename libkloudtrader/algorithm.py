from typing import Any, List
import random
import time
import datetime
import numpy as np
import pandas as pd
import libkloudtrader.stocks as stocks
from libkloudtrader.exceptions import InvalidAlgorithmMode, EmptySymbolBucket, InvalidDataFeedType
from libkloudtrader.enumerables import Data_Types
import libkloudtrader.processing as processing
from libkloudtrader.logs import start_logger
import libkloudtrader.backtest as bt
import libkloudtrader.crypto as crypto
import libkloudtrader.analysis as analysis
from tqdm import tqdm



#pd.set_option('display.max_columns', None)  # or 1000
#pd.set_option('display.max_rows', None)  # or 1000
#pd.set_option('display.max_colwidth', -1)  # or 199

logger = start_logger(__name__, ignore_module='libkloudtrader.analysis')


def run_backtest(strategy: str,
             symbol_bucket: List[str],
             data: str,
             start: Any,
             end: Any,
             data_interval:str="1d",
             preferred_price_point: str = 'close',
             preferred_benchmark: str = 'SPY',
             initial_capital: float = 100000,
             commission: float = 0,
             slippage=True):
    """Backtester function"""
    try:
        logger.info(
            'Starting Backtest for {} from {} to {} with initial capital = {}'.
            format(strategy.__name__, start, end, initial_capital))
        data_to_backtest_on = Data_Types[data].value
        for symbol in symbol_bucket:
            data_batch = data_to_backtest_on(symbol=symbol,
                                             start=start,
                                             end=end,interval=data_interval
                                             )
            batch = processing.Buffer(len(data_batch), dtype=object)
            backtest=bt.Backtest(capital=100000,commission=1,enable_slippage=True)
            for datetime, bar in data_batch.iterrows():
                batch.append(bar)
                backtest.update_bar(datetime,bar)
                data_batch = pd.DataFrame(batch)
                
                locals()['strategy'](backtest,data_batch)
            
            print(backtest.get_trade_log)
            del backtest
            
        
        '''
        for symbol in symbol_bucket:
            data_batch = data_to_backtest_on(symbol,
                                             start,
                                             end,
                                             interval=data_interval)
            for symbol in symbol_bucket:

              
                a = bt.Backtest(locals()['strategy'](data_batch),
                                preferred_price_point)
                print(a.preferred_price_point)
                
                signals=locals()['strategy'](data_batch)
                df=pd.DataFrame()
                df['buy']=signals['buy']
                df['sell']=signals['sell']
                df['short']=signals['short']
                df['cover']=signals['cover']
                '''
                #bt = Backtest(locals()['strategy'](data_batch), strategy.__name__)
                #df=bt.signals
                #df['positions']=bt.positions
                #df['price']=bt.trades['price']
                #df['trade volume']=bt.trades['vol']
                #df['trade_price']=bt.trade_price
                #df['equity']=bt.equity
                #df['trades']=bt.trades
                #df['positions in '+symbol]=100*df['positions']
                #print(bt.trades)

        #logger.info("Received Signals from {}".format(strategy.__name__))

    except (KeyboardInterrupt, SystemExit):
        print('\n')
        logger.critical("User's keyboard prompt stopped {}".format(
            strategy.__name__))
    except Exception as exception:
        logger.critical('Exiting {}...‼️'.format(strategy.__name__))
        logger.error(
            'Oops! Something went wrong while your algorithm was being backtested. ⚠️'
        )
        raise exception
        exit()

    #print(return_data_from_enum(a,symbol,start, end))
    #print(locals()[a](symbol, start, end))


def run_live(strategy: str,
               symbol_bucket: list,
               data_feed_type: str,
               exempted_states: list = [''],
               exempted_days:list=[''],
               exempted_dates:list=[''],
               batch_size: int = 1000,
               data_feed_delay: float = 1.0,
               fake_feed: bool = False):
    try:
        logger.info("{} is now entering the live markets. 📈\n".format(
            strategy.__name__))
        [x.lower() for x in exempted_states]
        [x.lower() for x in exempted_days]
        if isinstance(symbol_bucket, list):
            symbol_bucket = np.array(symbol_bucket)
        elif type(symbol_bucket) not in (numpy.ndarray, list):
            raise TypeError('Symbol bucket must be a list or numpy array')
        if data_feed_type not in ('CRYPTO_live_feed', 'US_STOCKS_live_feed',
                                  'CRYPTO_live_feed_level2'):
            raise InvalidDataFeedType(
                'This Data Feed is not available for live trading.'
            )
        if data_feed_type in ("CRYPTO_live_feed", 'CRYPTO_live_feed_level2'):
            data_feed_delay = crypto.exchange_attribute('rateLimit')
        data_feed = Data_Types[data_feed_type].value
        while stocks.intraday_status()['state'] not in exempted_states: #and datetime.datetime.now().strftime("%A").lower() not in exempted_days:
            batch = processing.Buffer(batch_size, dtype=object)
            while len(batch) < batch_size:
                for symbol in symbol_bucket:
                    batch.append(data_feed(symbol, fake_feed=fake_feed))
                    data_batch = pd.DataFrame(batch)
                    locals()['strategy'](data_batch)
                    if len(batch) == batch_size:
                        batch.popleft()
                    time.sleep(data_feed_delay / 1000)
    except (KeyboardInterrupt, SystemExit):
        print('\n')
        logger.critical("User's keyboard prompt stopped {}".format(
            strategy.__name__))
    except Exception as exception:
        logger.critical('Exiting {}...‼️'.format(strategy.__name__))
        logger.error('Oops! Something went wrong ⚠️')
        raise exception
        exit()


'''
def generate_positions_and_handle_portfolio(symbol, signals, data, commission,
                                            initial_capital, quantity):
    try:
        initial_capital = float(initial_capital)
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions['Positions in' + " " +
                  symbol] = (quantity * signals['signal']) + commission
        portfolio = positions.multiply(data['close'], axis=0)
        poss_diff = positions.diff()
        portfolio['holdings'] = (positions.multiply(data['close'],
                                                    axis=0)).sum(axis=1)
        return portfolio
    except Exception as exception:
        raise exception
'''
