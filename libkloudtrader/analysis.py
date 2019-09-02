"""Technical, portfolio, risk analysis APIs for your quantitative trading algorithms."""

from __future__ import absolute_import
from datetime import datetime
from typing import Any
from six.moves import range
import pandas as pd
import numpy as np
import talib
import empyrical
from libkloudtrader.logs import start_logger
from libkloudtrader.exceptions import AnalysisException

logger = start_logger(__name__)


'''Not in docs. helper functions'''

def check_for_period_error(data: Any, period: int):
    """
    Check for Period Error. Check if the period is larger than the number of data points in data
    """
    period = int(period)
    data_len = len(data)
    if data_len < period:
        logger.error('Oops! An error Occurred ⚠️')
        raise AnalysisException(
            "Length of Period is greater than number of data points in data.")


def check_period_type(period: int):
    """Check if given period is int"""
    if not isinstance(period, int):
        logger.error('Oops! An error Occurred ⚠️')
        raise AnalysisException("Period must be an integer.")


def fill_for_noncomputable_vals(input_data, result_data):
    """Fill non computable values"""
    non_computable_values = np.repeat(np.nan,
                                      len(input_data) - len(result_data))
    filled_result_data = np.append(non_computable_values, result_data)
    return filled_result_data


def check_inputs_length(*args):
    """Check if inputs have any length difference"""
    arrays_len = [len(arr) for arr in args]
    if not all(a == arrays_len[0] for a in arrays_len):
        logger.error('Oops! An error Occurred ⚠️')
        raise AnalysisException(
            "Mismatched data lengths. Please ensure that all data is of same length."
        )


def check_data_for_annual_trading_days(data: Any):
    """Check data for annual trading days"""
    if len(data) < 250 or len(data) > 257:
        logger.error('Oops! An error Occurred ⚠️')
        raise AnalysisException(
            "Data has more or less entries than one year should have. Please use returns() function to calculate returns for n number of days."
        )


"""In Docs"""


def accumulation_distribution_index(high, low, close, volume):
    """Accumulation/Distribution Index (ADI)"""
    try:
        logger.info('Calculating Accumulation/Distribution Index...')
        check_inputs_length(high, low, close, volume)
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.fillna(0.0)  # float division by zero
        ad = clv * volume
        ad = ad + ad.shift(1, fill_value=ad.mean())
        return pd.Series(ad)
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def awesome_oscillator(high, low, short_period=5, long_period=34):
    """Awesome Oscillator"""
    try:
        logger.info(
            'Calculating Awesome Oscillator for short period = {} and long period = {}'
            .format(short_period, long_period))
        check_inputs_length(high, low)
        for period in (short_period, long_period):
            check_period_type(period)
        mp = 0.5 * (high + low)
        ao = mp.rolling(short_period, min_periods=0).mean() - mp.rolling(
            long_period, min_periods=0).mean()
        return pd.Series(ao)
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def money_flow_index(high, low, close, volume, period):
    """Money Flow Index"""
    try:
        logger.info(
            "Calculating Money Flow Index for period = {}".format(period))
        check_period_type(period)
        check_inputs_length(high, low, close, volume)
        df = pd.DataFrame([high, low, close, volume]).T
        df.columns = ['High', 'Low', 'Close', 'Volume']

        # 1 typical price
        tp = (df['High'] + df['Low'] + df['Close']) / 3.0

        # 2 up or down column
        df['Up_or_Down'] = 0
        df.loc[(tp > tp.shift(1)), 'Up_or_Down'] = 1
        df.loc[(tp < tp.shift(1)), 'Up_or_Down'] = -1

        # 3 money flow
        mf = tp * df['Volume'] * df['Up_or_Down']

        # 4 positive and negative money flow with n periods
        n_positive_mf = mf.rolling(
            period).apply(lambda x: np.sum(np.where(x >= 0.0, x, 0.0)),
                          raw=True)
        n_negative_mf = abs(
            mf.rolling(
                period).apply(lambda x: np.sum(np.where(x < 0.0, x, 0.0)),
                              raw=True))
        # 5 money flow index
        mr = n_positive_mf / n_negative_mf
        mr = (100 - (100 / (1 + mr)))

        return mr
    except Exception as exception:
        raise exception


def relative_strength_index(data, period):
    """Relative Strength Index"""
    try:
        logger.info(
            'Calculating Relative Strength Index for peirod = {}'.format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        diff = data.diff(1)
        which_dn = diff < 0
        up, dn = diff, diff * 0
        up[which_dn], dn[which_dn] = 0, -up[which_dn]
        emaup = talib.EMA(up, period)
        emadn = talib.EMA(dn, period)
        rsi = 100 * emaup / (emaup + emadn)
        return rsi
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def stochastic_oscillator(high, low, close, period):
    """Stochastic Oscillator"""
    try:
        logger.info(
            'Calculating Stochastic Oscillator for period = {}'.format(period))
        smin = low.rolling(period).min()
        smax = high.rolling(period).max()
        stoch_k = 100 * (close - smin) / (smax - smin)
        return stoch_k
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def true_strength_index(data, high_period, low_period):
    """True Strength Index"""
    try:
        logger.info(
            'Calculating True Strength Index for high period = {} and low period = {}'
            .format(high_period, low_period))
        m = data - data.shift(1, fill_value=data.mean())
        m1 = m.ewm(high_period).mean().ewm(low_period).mean()
        m2 = abs(m).ewm(high_period).mean().ewm(low_period).mean()
        tsi = m1 / m2
        tsi *= 100
        return pd.Series(tsi, name='tsi')
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def ultimate_oscillator(high, low, close, short_period, medium_period,
                        long_period):
    """Ultimate Oscillator"""
    try:
        logger.info(
            'Calculating Ultimate Oscillator for short period = {}, medium period = {} and long period = {}'
            .format(short_period, medium_period, long_period))
        check_inputs_length(high, low, close)
        uo_data = talib.ULTOSC(high,
                               low,
                               close,
                               timeperiod1=short_period,
                               timeperiod2=medium_period,
                               timeperiod3=long_period)
        return uo_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def absolute_price_oscillator(data, short_period, long_period, matype=0):
    """Absolute Price Oscillator"""
    try:
        logger.info(
            'Calculating Absolute Price Oscillator for Short period = {} and Long period = {}'
            .format(short_period, long_period))
        for period in (short_period, long_period):
            check_period_type(period)
            check_for_period_error(data, period)
        apo_data = talib.APO(data, short_period, long_period, matype=matype)
        return apo_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def aroon(high, low, period):
    """Aroon"""
    try:
        check_period_type(period)
        check_inputs_length(high, low)
        logger.info('Calculating Aroon for period = {}'.format(period))
        aroondown, aroonup = talib.AROON(high, low, timeperiod=period)
        df = pd.DataFrame()
        df['aroondown'] = aroondown
        df['aroonup'] = aroonup
        df['aroon_oscillator'] = talib.AROONOSC(high, low, timeperiod=period)
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def average_directional_moving_index(high, low, close, period):
    """Average Directional Movement Index"""
    try:
        logger.info(
            'Calculating Average Directional Movement Index for period = {}'.
            format(period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        admi_data = talib.ADX(high, low, close, timeperiod=period)
        return admi_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def average_directional_moving_index_rating(high, low, close, period):
    """Average Directional Movement Index Rating"""
    try:
        logger.info(
            'Calculating Average Directional Movement Index Rating for period = {}'
            .format(period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        admir_data = talib.ADXR(high, low, close, timeperiod=period)
        return admir_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def average_price(open, high, low, close):
    try:
        """Average Price"""
        logger.info("Calculating Average Price...")
        check_inputs_length(high, low, close)
        avgprice_data = talib.AVGPRICE(open, high, low, close)
        return avgprice_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def average_true_range(high, low, close, period):
    """Average True Range"""
    try:
        logger.info(
            "Calculating Average True Range for period = {}".format(period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        atr_data = talib.ATR(high, low, close, timeperiod=period)
        return atr_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def normalized_average_true_range(high, low, close, period):
    try:
        """Normalized Average True Range"""
        logger.info(
            'Calculating Normalized Average True Range for period = {}'.format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        natr_data = talib.NATR(high, low, close, timeperiod=period)
        return natr_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def true_range(high, low, close):
    """True Range"""
    try:
        logger.info('Calculating True Range...')
        check_inputs_length(high, low, close)
        tr_data = talib.TRANGE(high, low, close)
        return tr_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def balance_of_power(open, high, low, close):
    """Balance of Power"""
    try:
        logger.info("Calculating balance of Power...")
        check_inputs_length(open, high, low, close)
        bop_data = talib.BOP(open, high, low, close)
        return bop_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def bollinger_bands(data, period=20, nbdevup=2, nbdevdn=2, matype=0):
    """Bollinger Bands"""
    try:
        logger.info(
            'Calculating Bollinger Bands for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        upperband, middleband, lowerband = talib.BBANDS(data,
                                                        timeperiod=period,
                                                        nbdevup=nbdevup,
                                                        nbdevdn=nbdevdn,
                                                        matype=matype)
        df = pd.DataFrame()
        df['upperband'] = upperband
        df['middleband'] = middleband
        df['lowerband'] = lowerband
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def chaikin_money_flow(high, low, close, volume, period):
    """Chaiking Money Flow"""
    try:
        logger.info(
            "Calculating Chaikin Money Flow for period = {}".format(period))
        check_period_type(period)
        check_inputs_length(high, low, close, volume)
        for data in (high, low, close, volume):
            check_for_period_error(data, period)
        mfv = ((close - low) - (high - close)) / (high - low)
        mfv = mfv.fillna(0.0)  # float division by zero
        mfv *= volume
        cmf = (mfv.rolling(period, min_periods=0).sum() /
               volume.rolling(period, min_periods=0).sum())
        return pd.Series(cmf)
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def chande_momentum_oscillator(data, period):
    """Chande Momentum Oscillator"""
    try:
        logger.info(
            "Calculating Chande Momentum Oscillator for period = {}".format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        cmo_data = talib.CMO(data, timeperiod=period)
        return cmo_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def commodity_channel_index(high, low, close, period):
    """Commodity Channel Index"""
    try:
        logger.info(
            "Calculating Commodity Channel Index for period = {}".format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        cci_data = talib.CCI(high, low, close, timeperiod=period)
        return cci_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def correlation_coefficient(high, low, period):
    """Correlation Coefficient"""
    try:
        logger.info(
            "Calculating Correlation Coefficient for period = {}".format(
                period))
        check_period_type(period)
        check_inputs_length(high, low)
        cor_co_data = talib.CORREL(high, low, timeperiod=period)
        return cor_co_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def cumulative_returns(daily_returns):
    """Cumulative Returns"""
    try:
        logger.info("Calculating Cumulative Returns...")
        cr = empyrical.cum_returns(daily_returns)
        return cr
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def daily_returns(data):
    """Daily Returns"""
    try:
        logger.info("Calculating Daily Returns...")
        dr_data = data.pct_change(1)
        return pd.Series(dr_data, name="daily_returns")
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def daily_log_returns(data):
    """Daily Log Returns"""
    try:
        logger.info("Calculating Daily Log Returns...")
        dlr = np.log(data).diff()
        dlr *= 100
        return pd.Series(dlr, name="daily_log_returns")
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def detrended_price_oscillator(data, period):
    """Detrended price oscillator"""
    try:
        logger.info(
            "Calculating Detrended Price Oscillator for period = {}".format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        dpo = data.shift(int((0.5 * period) + 1),
                         fill_value=data.mean()) - data.rolling(
                             period, min_periods=0).mean()
        return dpo
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def directional_movement_index(high, low, close, period):
    """Directional Movement Index"""
    try:
        logger.info(
            "Calculating Directional Movement Index for period = {}".format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        dmo_data = talib.DX(high, low, close, timeperiod=period)
        return dmo_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def donchian_channel(data, period):
    """Donchian Channels"""
    try:
        logger.info(
            "Calculating Donchian Channels for period = {}".format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        #dc high band
        dc_high_band = data.rolling(period, min_periods=0).max()

        #dc high band indicator
        df = pd.DataFrame([data]).transpose()
        df['hband'] = 0.0
        hband = data.rolling(period).max()
        df.loc[data >= hband, 'hband'] = 1.0
        dc_high_band_indicator = df['hband']

        #dc low band
        dc_low_band = data.rolling(period, min_periods=0).min()

        #dc low band indicator
        df = pd.DataFrame([data]).transpose()
        df['lband'] = 0.0
        lband = data.rolling(period).min()
        df.loc[data <= lband, 'lband'] = 1.0
        dc_low_band_indicator = df['lband']

        df = pd.DataFrame()
        df['dc_high_band'] = dc_high_band
        df['dc_high_band_indicator'] = dc_high_band_indicator
        df['dc_low_band'] = dc_low_band
        df['dc_low_band_indicator'] = dc_low_band_indicator
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def double_ema(data, period):
    """Double EMA"""
    try:
        logger.info(
            "Calculating Double Exponential Moving Average for period = {}".
            format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        dema_data = talib.DEMA(data, period)
        return dema_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def ease_of_movement(high, low, close, volume, period):
    """Ease of movement"""
    try:
        logger.info(
            "Calculating Ease of Movement for period = {}".format(period))
        check_period_type(period)
        check_inputs_length(high, low, close, volume)
        emv = (high.diff(1) + low.diff(1)) * (high - low) / (2 * volume)
        emv = emv.rolling(period, min_periods=0).mean()
        return emv
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def force_index(close, volume, period):
    """Force Index"""
    try:
        logger.info('Calculating Force Index for period = {}'.format(period))
        check_period_type(period)
        check_inputs_length(close, volume)
        fi = close.diff(period) * volume.diff(period)
        return fi
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def ema(data, period):
    """EMA"""
    try:
        logger.info(
            "Calculating Exponential Moving Average for period = {}".format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        ema_data = talib.EMA(data, timeperiod=period)
        return ema_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def ichimoku_cloud(high, low, short_period, medium_period, long_period):
    """Ichimoku Cloud"""
    try:
        logger.info(
            "Calculating Ichimoku Cloud for short period = {}, medium period = {} and long period = {}"
            .format(short_period, medium_period, long_period))
        for period in (short_period, long_period, medium_period):
            check_period_type(period)
        check_inputs_length(high, low)
        conv = 0.5 * (high.rolling(short_period, min_periods=0).max() +
                      low.rolling(short_period, min_periods=0).min())
        base = 0.5 * (high.rolling(medium_period, min_periods=0).max() +
                      low.rolling(medium_period, min_periods=0).min())
        ia = 0.5 * (conv + base)
        ib = 0.5 * (high.rolling(long_period, min_periods=0).max() +
                    low.rolling(long_period, min_periods=0).min())
        df = pd.DataFrame()
        df['ichimoku_cloud_a'] = ia
        df['ichimoku_cloud_b'] = ib
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def kaufman_adaptive_moving_average(data, period):
    '''Kaufman Adaptive Moving Average'''
    try:
        logger.info(
            'Calculating Kaufman Adaptive Moving Average for period = {}'.
            format(period))
        check_period_type(period)
        check_inputs_length(data)
        kama_data = talib.KAMA(data, timeperiod=period)
        return kama_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def keltner_channels(high, low, close, period):
    """Keltner Channels"""
    try:
        logger.info(
            "Calculating Kelnter Channels for period = {}".format(period))
        check_period_type(period)
        check_inputs_length(high, low, close)

        df = pd.DataFrame()
        kch = ((4 * high) - (2 * low) + close) / 3.0
        df['keltner_channel_highband'] = kch.rolling(period,
                                                     min_periods=0).mean()
        kcc = (high + low + close) / 3.0
        df['keltner_channel_central'] = kcc.rolling(period,
                                                    min_periods=0).mean()
        kcl = ((-2 * high) + (4 * low) + close) / 3.0
        df['keltner_channel_lowband'] = kcl.rolling(period,
                                                    min_periods=0).mean()
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def know_sure_thing(data: Any, r1: int, r2: int, r3: int, r4: int, n1: int,
                    n2: int, n3: int, n4: int, nsig: int):
    """Know Sure Thing"""
    try:
        logger.info("Calculating Know Sure Thing...")
        for period in (r1, r2, r3, r4, n1, n2, n3, n4, nsig):
            check_period_type(period)
            check_for_period_error(data, period)
        rocma1 = ((data - data.shift(r1, fill_value=data.mean())) /
                  data.shift(r1, fill_value=data.mean())).rolling(
                      n1, min_periods=0).mean()
        rocma2 = ((data - data.shift(r2, fill_value=data.mean())) /
                  data.shift(r2, fill_value=data.mean())).rolling(
                      n2, min_periods=0).mean()
        rocma3 = ((data - data.shift(r3, fill_value=data.mean())) /
                  data.shift(r3, fill_value=data.mean())).rolling(
                      n3, min_periods=0).mean()
        rocma4 = ((data - data.shift(r4, fill_value=data.mean())) /
                  data.shift(r4, fill_value=data.mean())).rolling(
                      n4, min_periods=0).mean()
        kst = 100 * (rocma1 + 2 * rocma2 + 3 * rocma3 + 4 * rocma4)
        return kst
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def linear_regression(data, period):
    """Linear Regression"""
    try:
        logger.info(
            'Calculating Linear Regression for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        lr_data = talib.LINEARREG(data, timeperiod=period)
        return lr_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def linear_regression_angle(data, period):
    """Linear Regression Angle"""
    try:
        logger.info(
            'Calculating Linear Regression Angle for period = {}'.format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        lra_data = talib.LINEARREG_ANGLE(data, timeperiod=period)
        return lra_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def linear_regression_intercept(data, period):
    """Linear Regression Intercept"""
    try:
        logger.info(
            'Calculating Linear Regression Intercept for period = {}'.format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        lri_data = talib.LINEARREG_INTERCEPT(data, timeperiod=period)
        return lri_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def linear_regression_slope(data, period):
    """Linear Regression Slope"""
    try:
        logger.info(
            'Calculating Linear Regression Slope for period = {}'.format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        lrs_data = talib.LINEARREG_SLOPE(data, timeperiod=period)
        return lrs_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def macd(data, n_sign, short_period=12, long_period=26, fillna=False):
    """Moving Average Convergence Divergence"""
    try:
        logger.info(
            "Calculating Moving Average Convergence Divergence for short period = {} and long period = {}"
            .format(short_period, long_period))
        for period in (short_period, long_period):
            check_period_type(period)
            check_for_period_error(data, period)
        df = pd.DataFrame()
        emafast = talib.EMA(data, short_period)
        emaslow = talib.EMA(data, long_period)
        df['macd'] = emafast - emaslow
        df['macd_signal'] = talib.EMA(df['macd'], n_sign)
        df['macd_difference'] = df['macd'] - df['macd_signal']
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def mass_index(high, low, short_period, long_period):
    """Mass Index"""
    try:
        logger.info(
            "Calculating mass Index for short period = {} and long period = {}"
            .format(short_period, long_period))
        for period in (short_period, long_period):
            check_period_type(period)
        check_inputs_length(high, low)
        amplitude = high - low
        ema1 = talib.EMA(amplitude, short_period)
        ema2 = talib.EMA(ema1, short_period)
        mass = ema1 / ema2
        mass = mass.rolling(long_period, min_periods=0).sum()
        return mass
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def midpoint_over_period(data, period):
    """Midpoint over period"""
    try:
        logger.info(
            'Calculating Midpoint Over Period for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        mop = talib.MIDPOINT(data, timeperiod=period)
        return mop
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def midpoint_price_over_period(high, low, period):
    """Midpoint price over period"""
    try:
        logger.info(
            'Calculating Midpoint Price Over Period for period = {}'.format(
                period))
        check_period_type(period)
        for data in (high, low):
            check_for_period_error(data, period)
        check_inputs_length(high, low)
        mpop = talib.MIDPRICE(high, low, timeperiod=period)
        return mpop
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def minus_directional_indicator(high, low, close, period):
    """Minus Directional Indicator"""
    try:
        logger.info(
            'Calculating Minus Directional Indicator for period = {}'.format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        mdi_data = talib.MINUS_DI(high, low, close, timeperiod=period)
        return mdi_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def minus_directional_movement(high, low, close, period):
    """Minus Directional Movement"""
    try:
        logger.info(
            'Calculating Minus Directional Movement for period = {}'.format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        mdm_data = talib.MINUS_DM(high, low, timeperiod=period)
        return mdm_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def median_price(high, low):
    """Calculating Median Price"""
    try:
        logger.info("Calculating Median Price...")
        mp_data = talib.MEDPRICE(high, low)
        check_inputs_length(high, low)
        return mp_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def momentum(data, period):
    """Momentum"""
    try:
        logger.info('Calculating Momentum for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        momentum_data = talib.MOM(data, timeperiod=period)
        return momentum_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def ma(data, period, matype=0):
    """Moving Average"""
    try:
        logger.info(
            'Calculating Moving Average for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        ma_data = talib.MA(data, timeperiod=period, matype=matype)
        return ma_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def negative_volume_index(data, volume):
    """Negative Volume Index"""
    try:
        logger.info('Calculating Negative Volume Index...')
        check_inputs_length(data, volume)
        price_change = data.pct_change()
        vol_decrease = (volume.shift(1) > volume)
        nvi = pd.Series(data=np.nan,
                        index=data.index,
                        dtype='float64',
                        name='nvi')
        nvi.iloc[0] = 1000
        for i in range(1, len(nvi)):
            if vol_decrease.iloc[i]:
                nvi.iloc[i] = nvi.iloc[i - 1] * (1.0 + price_change.iloc[i])
            else:
                nvi.iloc[i] = nvi.iloc[i - 1]
        return pd.Series(nvi)
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hilbert_transform_inst_trendline(data):
    """Hilbert Transform - Instantaneous Trendline"""
    try:
        logger.info(
            'Calculating Hilbert Transform - Instantaneous Trendline...')
        htit_data = talib.HT_TRENDLINE(data)
        return htit_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hilbert_transform_dom_cyc_per(data):
    """Hilbert Transform - Dominant Cycle Period"""
    try:
        logger.info('Calculating Hilbert Transform - Dominant Cycle Period')
        htdcp_data = talib.HT_DCPERIOD(data)
        return htdcp_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hilbert_transform_dom_cyc_phase(data):
    """Hilbert Transform - Dominant Cycle Phase"""
    try:
        logger.info('Calculating Hilbert Transform - Dominant Cycle Phase')
        htdcp_data = talib.HT_DCPHASE(data)
        return htdcp_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hilbert_transform_phasor_components(close):
    """Hilbert Transform - Phasor Components"""
    try:
        logger.info("Calculating Hilbert Transform - Phasor Components...")
        inphase_data, quadrature_data = talib.HT_PHASOR(close)
        df = pd.DataFrame()
        df['inphase'] = inphase_data
        df['quadrature'] = quadrature_data
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hilbert_transform_sine_wave(data):
    """Hilbert Transform - Sine Wave"""
    try:
        logger.info("Calculating Hilbert Transform - Sine Wave...")
        sine_data, leadsine_data = talib.HT_SINE(data)
        df = pd.DataFrame()
        df['sine'] = sine_data
        df['leadsine'] = leadsine_data
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hilbert_transform_trend_vs_cycle_mode(data):
    """Hilbert Transform - Trend vs cycle mode"""
    try:
        logger.info("Calculating Hilbert Transform - Trend vs cycle mode...")
        httc_data = talib.HT_TRENDMODE(data)
        return httc_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def on_balance_volume(data, volume):
    """On Balance Volume"""
    try:
        logger.info("Calculating On Balance Volume... ")
        check_inputs_length(data, volume)
        obv_data = talib.OBV(data, volume)
        return obv_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def parabolic_sar(high, low, acceleration=0, maximum=0):
    """Parabolic SAR"""
    try:
        logger.info('Calculating Parabolic SAR...')
        check_inputs_length(high, low)
        ps_data = talib.SAR(high, low, acceleration, maximum)
        return ps_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def percentage_price_oscillator(data, short_period, long_period, matype=0):
    """Percentage Price Oscillator"""
    try:
        logger.info(
            'Calculating Percentage Price Oscillator for short period = {} and long period = {}'
            .format(short_period, long_period))
        for period in (short_period, long_period):
            check_period_type(period)
            check_for_period_error(data, period)
        ppo_data = talib.PPO(data, short_period, long_period, matype)
        return ppo_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def plus_directional_indicator(high, low, close, period):
    """Plus Directional Indicator"""
    try:
        logger.info(
            'Calcluating Plus Directional Indicator for period = {}'.format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        pdi_data = talib.PLUS_DI(high, low, close, timeperiod=period)
        return pdi_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def plus_directional_movement(high, low, close, period):
    """Plus Directional Movement"""
    try:
        logger.info(
            'Calcluating Plus Directional Movement for period = {}'.format(
                period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        pdm_data = talib.PLUS_DM(high, low, timeperiod=period)
        return pdm_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def rate_of_change(data, period):
    """Rate of Change"""
    try:
        logger.info(
            "Calculating Rate of Change for period = {}".format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        df = pd.DataFrame()
        df['rate_of_change'] = talib.ROC(data, timeperiod=period)
        df['rate_of_change_precentage'] = talib.ROCP(data, timeperiod=period)
        df['rate_of_change_ratio'] = talib.ROCR(data, timeperiod=period)
        df['rate_of_change_ratio_100_scale'] = talib.ROCR100(data,
                                                             timeperiod=period)
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


#SMA
def sma(close, period):
    try:
        sma_data = talib.SMA(close, timeperiod=period)
        return sma_data
    except Exception as exception:
        raise exception


def standard_deviation(data: Any):
    """Standard Deviation"""
    try:
        logger.info("Calculating Standar Deviation...")
        sd_data = data.std()
        return sd_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def moving_standard_deviation(close, period, nbdev=1):
    try:

        pass
    except Exception as exception:
        raise exception


def stochastic_rsi(data,
                   period,
                   fast_period1=5,
                   fast_period2=3,
                   fastd_matype=0):
    """Stochastic RSI"""
    try:
        logger.info(
            'Calculating Stochastic RSI for period = {}, fast_period1 = {}, fast_period2 = {}'
            .format(period, fast_period1, fast_period2))
        for a in (period, fast_period1, fast_period2):
            check_period_type(a)
            check_for_period_error(data, a)
        fastk_data, fastd_data = talib.STOCHRSI(data, period, fast_period1,
                                                fast_period2, fastd_matype)
        df = pd.DataFrame()
        df['fast_period1'] = fastk_data
        df['fast_period2'] = fastd_data
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def time_series_forecast(data, period):
    """Time Series Forecast"""
    try:
        logger.info(
            'Calculating Time Series Forecast for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        tsf_data = talib.TSF(data, timeperiod=period)
        return tsf_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def trix(data, period):
    """TRIX"""
    try:
        logger.info('Calculating Trix for period = {}'.format(period))
        trix_data = talib.TRIX(data, timeperiod=period)
        check_period_type(period)
        check_for_period_error(data, period)
        return trix_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def triangular_ma(data, period):
    """Triangular Moving average"""
    try:
        logger.info(
            'Calculating Triangular Moving Average for period = {}'.format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        tma_data = talib.TRIMA(data, timeperiod=period)
        return tma_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def triple_ema(data, period):
    """Triple Exponential Moving Average"""
    try:
        logger.info(
            "Calculating Triple Exponential Moving Average for period = {}".
            format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        tema_data = talib.TEMA(data, timeperiod=period)
        return tema_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def typical_price(high, low, close):
    """Typical Price"""
    try:
        logger.info('Calculating Typical Price...')
        check_inputs_length(high, low, close)
        tp_data = talib.TYPPRICE(high, low, close)
        return tp_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def variance(data: Any):
    """Variance"""
    try:
        logger.info('Calculating Variance...')
        var = data.var()
        return var
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


#variance
def moving_variance(data, period, nbdev=1):
    try:
        var_data = talib.VAR(data, timeperiod=period, nbdev=nbdev)
        return var_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def vortex_indicator(high: Any, low: Any, close: Any, period: int):
    """Vortex Indicator"""
    try:
        logger.info(
            'Calculating Vortex Indicator for period = {}'.format(period))
        check_period_type(period)
        check_inputs_length(high, low, close)
        df = pd.DataFrame()
        tr = (high.combine(close.shift(1, fill_value=close.mean()), max) -
              low.combine(close.shift(1, fill_value=close.mean()), min))
        trn = tr.rolling(period).sum()
        vmp = np.abs(high - low.shift(1, fill_value=low.mean()))
        vmm = np.abs(low - high.shift(1, fill_value=high.mean()))
        vip = vmp.rolling(period, min_periods=0).sum() / trn
        df['vortex_inidicator_positive'] = vip
        tr = high.combine(close.shift(1), max) - low.combine(
            close.shift(1), min)
        trn = tr.rolling(period).sum()
        vmp = np.abs(high - low.shift(1))
        vmm = np.abs(low - high.shift(1))
        vin = vmm.rolling(period).sum() / trn
        df['vortex_indicator_negative'] = vin
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def weighted_close_price(high, low, close):
    """Weighted Close Price"""
    try:
        logger.info("Calculating Weighted Close Price...")
        check_inputs_length(high, low, close)
        wcp_data = talib.WCLPRICE(high, low, close)
        return wcp_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def williams_r(high, low, close, period):
    """Williams' %R"""
    try:
        logger.info("Calculating Williams' %R for period = {}")
        wr_data = talib.WILLR(high, low, close, timeperiod=period)
        return wr_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def wma(data, period):
    """Weighted Moving Average"""
    try:
        logger.info(
            'Calculating Weighted Moving Average for period = {}'.format(
                period))
        check_period_type(period)
        check_for_period_error(data, period)
        wma_data = talib.WMA(data, timeperiod=period)
        return wma_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


#Two Crows
def two_crows(open, high, low, close):
    try:
        tc_data = talib.CDL2CROWS(open, high, low, close)
        return tc_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def annual_return(data):
    """Annual Return (in percent)"""
    try:
        check_data_for_annual_trading_days(data)
        trading_days = len(data)
        logger.info(
            'Calculating Annual return. Number of trading days in provided data: {}'
            .format(trading_days))
        df = pd.DataFrame()
        df['daily_returns'] = daily_returns(data)
        mean_daily_returns = df['daily_returns'].mean()
        annual_return = mean_daily_returns * trading_days
        return annual_return
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def returns(data):
    """Returns for any number of days"""
    try:
        trading_days = len(data)
        logger.info(
            "Calculating Returns for {} trading days".format(trading_days))
        df = pd.DataFrame()
        df['daily_returns'] = data.pct_change(1)
        mean_daily_returns = df['daily_returns'].mean()
        returns_data = mean_daily_returns * trading_days
        return returns_data * 100
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def annual_volatility(data):
    """Annual Volatility"""
    try:
        trading_days = len(data)
        logger.info(
            "Calculating Annual Volatility. Number of trading days in provided data: {}"
            .format(trading_days))
        check_data_for_annual_trading_days(data)
        dr_data = data.pct_change(1)
        av_data = np.std(dr_data) * np.sqrt(trading_days)
        return av_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def volatility(daily_returns: Any):
    """Volatility"""
    try:
        logger.info('Calculating Volatility...')
        trading_days = len(daily_returns)
        av_data = daily_returns.std() * np.sqrt(trading_days)
        return av_data
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def moving_volatility(daily_returns, period):
    """Moving volatility"""
    try:
        logger.info(
            'Calculating Moving volatility for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(daily_returns, period)
        df = pd.DataFrame()
        df['moving_volatility'] = daily_returns.rolling(
            period).std() * np.sqrt(period)
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def chaikin_oscillator(high,
                       low,
                       close,
                       volume,
                       short_period=3,
                       long_period=10):
    """Chaiking oscillator"""
    try:
        logger.info(
            'Calculating Chaikin Oscillator for short period = {} and long period = {}'
            .format(short_period, long_period))
        check_inputs_length(high, low, close, volume)
        for period in (short_period, long_period):
            check_period_type(period)
        df = pd.DataFrame()
        df['chaikin_ad_line'] = talib.AD(high, low, close, volume)
        df['chaikin_oscillator'] = talib.ADOSC(high,
                                               low,
                                               close,
                                               volume,
                                               fastperiod=short_period,
                                               slowperiod=long_period)
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def coppock_curve(data, period):
    """Coppock Curve"""
    try:
        logger.info("Calculating Cappock Curve for period = {}".format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        M = data.diff(int(period * 11 / 10) - 1)
        N = data.shift(int(period * 11 / 10) - 1)
        ROC1 = M / N
        M = data.diff(int(period * 14 / 10) - 1)
        N = data.shift(int(period * 14 / 10) - 1)
        ROC2 = M / N
        Copp = pd.Series((ROC1 + ROC2).ewm(span=period,
                                           min_periods=period).mean(),
                         name="coppock_curve")
        return Copp
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def hull_moving_average(data, period):
    '''Hull moving average
    Formula:
    HMA = WMA(2*WMA(period/2) - WMA(period)), sqrt(period)
    '''
    try:
        logger.info(
            'Calculating Hull Moving Average for period = {}'.format(period))
        check_period_type(period)
        check_for_period_error(data, period)
        hma = wma(2 * wma(data, int(period / 2)) - wma(data, period),
                  int(np.sqrt(period)))
        return hma
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def volume_price_trend(close, volume):
    """Volume Price Trend"""
    try:
        logger.info('Calculating Volume Price Trend...')
        check_inputs_length(close, volume)
        vpt = volume * ((close - close.shift(1)) / close.shift(1))
        df = vpt.shift(1) + vpt
        return df
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def volume_adjusted_moving_average(data, volume, period):
    """Volume adjusted moving average"""
    try:
        logger.info(
            "Calcilating Volume adjusted moving average for period = {}".
            format(period))
        avg_vol = np.mean(volume)
        vol_incr = avg_vol * 0.67
        vol_ratio = [val / vol_incr for val in volume]
        data_vol = np.array(data) * vol_ratio
        vama = [
            sum(data_vol[idx + 1 - period:idx + 1]) / period
            for idx in range(period - 1, len(data))
        ]
        vama = fill_for_noncomputable_vals(data, vama)
        return pd.Series(vama, index=data.index)
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def sharpe_ratio(daily_returns):
    """Sharpe Ratio"""
    try:
        logger.info('Calculating Sharpe Ratio...')
        trading_days = len(daily_returns)
        sqrt = np.sqrt(trading_days)
        avg_returns = np.mean(daily_returns)
        std_returns = np.std(daily_returns)
        sharpe_ratio = (sqrt * avg_returns) / std_returns
        return sharpe_ratio
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def annual_sharpe_ratio(data):
    """Annual Sharpe Ratio"""
    try:
        logger.info(
            'Calculating Annual Sharpe Ratio. Number of trading days in provided data: {}'
            .format(len(data)))
        check_data_for_annual_trading_days(data)
        sqrt = np.sqrt(len(data))
        avg_returns = np.mean(daily_returns(data))
        std_returns = np.std(daily_returns(data))
        sharpe_ratio = (sqrt * avg_returns) / std_returns
        return sharpe_ratio
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def vwap(high, low, close, volume):
    """Volume weighted price average"""
    try:
        logger.info('Calculating Volume Weighted Average Price...')
        check_inputs_length(high, low, close, volume)
        vwap = np.cumsum(volume * (high + low) / 2) / np.cumsum(volume)
        return pd.Series(vwap)
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception


def sortino_ratio(daily_returns,
                  required_return=0,
                  period='daily',
                  annualization=None,
                  out=None,
                  _downside_risk=None):
    """Sortino Ratio"""
    try:
        logger.info("Calculating Sortino Ratio...")
        sr_data = empyrical.sortino_ratio(daily_returns,
                                          required_return,
                                          period=period,
                                          annualization=annualization,
                                          out=out,
                                          _downside_risk=_downside_risk)
        return sr_data
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def calmar_ratio(daily_returns, period="daily"):
    """Calmar Ratio"""
    try:
        logger.info('Calculating Calmar Ratio...')
        calmar = empyrical.calmar_ratio(daily_returns, period=period)
        return calmar
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


#Skew
def skewness(data: Any):
    try:
        logger.info("Calculating Skewness...")
        return data.skew()
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def kurtosis(data: Any):
    """Kurtosis"""
    try:
        logger.info('Calculating Kurtosis...')
        return data.kurtosis()
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def omega_ratio(daily_returns,
                risk_free=0.0,
                required_return=0.0,
                trading_days=252):
    """Omega Ratio"""
    try:
        logger.info("Calculating Omega Ratio...")
        omr_data = empyrical.omega_ratio(daily_returns,
                                         risk_free=risk_free,
                                         required_return=required_return,
                                         annualization=trading_days)
        return omr_data
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def tail_ratio(daily_returns):
    """Tail Ratio"""
    try:
        logger.info("Calculating Tail Ratio...")
        tr_data = empyrical.tail_ratio(daily_returns)
        return tr_data
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def alpha(daily_returns: Any,
          benchmark_daily_returns: Any,
          risk_free: float = 0.0,
          period: str = 'daily',
          annualization: Any = None,
          _beta: Any = None):
    """Alpha"""
    try:
        logger.info('Calculating Alpha...')
        check_inputs_length(daily_returns, benchmark_daily_returns)
        alpha_data = empyrical.alpha(daily_returns,
                                     benchmark_daily_returns,
                                     risk_free=risk_free,
                                     period=period,
                                     annualization=annualization,
                                     _beta=_beta)
        return alpha_data
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def beta(daily_returns, benchmark_daily_returns, risk_free=0.0):
    """Beta"""
    try:
        logger.info('Calculating Beta...')
        check_inputs_length(daily_returns, benchmark_daily_returns)
        beta_data = empyrical.beta(daily_returns,
                                   benchmark_daily_returns,
                                   risk_free=risk_free)
        return beta_data
    except Exception as exception:
        raise exception


#Adjusted returns
def adjusted_returns(returns, adjustment_factor):
    if isinstance(adjustment_factor, (float, int)) and adjustment_factor == 0:
        return returns.copy()
    return returns - adjustment_factor


def information_ratio(daily_returns, benchmark_daily_returns):
    """Information Ratio"""
    try:
        logger.info('Calculating Information Raito...')
        check_inputs_length(daily_returns, benchmark_daily_returns)
        trading_days = len(daily_returns)
        rets = daily_returns.mean() * trading_days
        benchmark_rets = benchmark_daily_returns.mean() * trading_days
        return_difference = rets - benchmark_rets
        volatility = daily_returns.std() * np.sqrt(trading_days)
        information_ratio = return_difference / volatility
        return information_ratio
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def cagr(start_value, end_value, period_in_years):
    """CAGR(in percent)"""
    try:
        logger.info('Calculating CAGR for years = {}'.format(period_in_years))
        cagr_data = (end_value / start_value)**(1 / period_in_years) - 1
        return cagr_data * 100
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def downside_risk(daily_returns,
                  required_return=0,
                  period='daily',
                  annualization=None):
    """Downside Risk"""
    try:
        logger.info('Calculating Downside Risk...')
        dr_data = empyrical.downside_risk(daily_returns,
                                          required_return=required_return,
                                          period=period,
                                          annualization=annualization)
        return dr_data
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def value_at_risk(daily_returns, confidence_level: int):
    """Value at risk"""
    try:
        logger.info(
            'Calculating Value at Risk for confidence level = {}'.format(
                confidence_level))
        if not isinstance(confidence_level, int) or isinstance(
                confidence_level, float):
            raise AnalysisException(
                'Confidence level must be an integer or floating point number.'
            )
        sorted_rets = sorted(daily_returns)
        varg = np.percentile(sorted_rets, 100.0 - confidence_level)

        return varg
        '''
        mean = np.mean(daily_returns)
        std_dev = np.std(daily_returns)
        var_90 = scstat.norm.ppf(1 - 0.9, mean, std_dev)
        var_95 = scstat.norm.ppf(1 - 0.95, mean, std_dev)
        var_99 = scstat.norm.ppf(1 - 0.99, mean, std_dev)
        if tabular == True:
            data = tabulate(
                [["90%", var_90], ["95%", var_95], ["99%", var_99]],
                headers=["Confidence Level", "Value at Risk"])
            return data
        else:
            data = {"90%": var_90, "95%": var_95, "99%": var_99}
            return data
        '''
    except Exception as exception:
        logger.error('Oops! An Error Occurred ⚠️')
        raise exception


def vertical_horizontal_filter(data: Any, period: int):
    """
    Vertical Horizontal Filter.
    Formula:
    ABS(pHIGH - pLOW) / SUM(ABS(Pi - Pi-1))
    """
    try:
        logger.info(
            'Calculating Vertical Horizontal Filter for period = {}'.format(
                period))
        check_for_period_error(data, period)
        vhf = [
            abs(
                np.max(data[idx + 1 - period:idx + 1]) -
                np.min(data[idx + 1 - period:idx + 1])) / sum([
                    abs(data[idx + 1 - period:idx + 1][i] -
                        data[idx + 1 - period:idx + 1][i - 1])
                    for i in range(0, len(data[idx + 1 - period:idx + 1]))
                ]) for idx in range(period - 1, len(data))
        ]
        vhf = fill_for_noncomputable_vals(data, vhf)
        vhf = pd.DataFrame(vhf, columns=['vhf']).set_index(data.index)
        return vhf
    except Exception as exception:
        logger.error('Oops! An error Occurred ⚠️')
        raise exception
