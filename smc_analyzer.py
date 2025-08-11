import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import asyncio

from market_sentiment import MarketSentimentAnalyzer  # import the new sentiment analyzer


class SMCAnalyzer:
    """
    Smart Money Concepts (SMC) and Inner Circle Trader (ICT) Logic Implementation
    Now integrated with Market Sentiment for combined signals.
    """

    def __init__(self):
        self.swing_length = 5
        self.sentiment_analyzer = MarketSentimentAnalyzer()

    def identify_market_structure(self, df):
        """Identify Break of Structure (BOS) and Change of Character (CHoCH)"""
        try:
            swing_highs = self.find_swing_highs(df)
            swing_lows = self.find_swing_lows(df)

            structure = {
                'trend': 'NEUTRAL',
                'bos_detected': False,
                'choch_detected': False
            }

            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                recent_highs = swing_highs[-2:]
                recent_lows = swing_lows[-2:]

                # Check for Higher Highs and Higher Lows (Bullish trend)
                if (recent_highs[1]['price'] > recent_highs[0]['price'] and
                        recent_lows[1]['price'] > recent_lows[0]['price']):
                    structure['trend'] = 'BULLISH'
                    structure['bos_detected'] = True

                # Check for Lower Highs and Lower Lows (Bearish trend)
                elif (recent_highs[1]['price'] < recent_highs[0]['price'] and
                      recent_lows[1]['price'] < recent_lows[0]['price']):
                    structure['trend'] = 'BEARISH'
                    structure['bos_detected'] = True

            return structure

        except Exception as e:
            logging.error(f"Error in market structure analysis: {e}")
            return {'trend': 'NEUTRAL', 'bos_detected': False, 'choch_detected': False}

    def find_swing_highs(self, df):
        """Find swing highs in the data"""
        swing_highs = []
        for i in range(self.swing_length, len(df) - self.swing_length):
            current_high = df['High'].iloc[i]
            is_swing_high = True

            for j in range(i - self.swing_length, i + self.swing_length + 1):
                if j != i and df['High'].iloc[j] >= current_high:
                    is_swing_high = False
                    break

            if is_swing_high:
                swing_highs.append({
                    'index': i,
                    'price': current_high,
                    'time': df.index[i]
                })

        return swing_highs

    def find_swing_lows(self, df):
        """Find swing lows in the data"""
        swing_lows = []
        for i in range(self.swing_length, len(df) - self.swing_length):
            current_low = df['Low'].iloc[i]
            is_swing_low = True

            for j in range(i - self.swing_length, i + self.swing_length + 1):
                if j != i and df['Low'].iloc[j] <= current_low:
                    is_swing_low = False
                    break

            if is_swing_low:
                swing_lows.append({
                    'index': i,
                    'price': current_low,
                    'time': df.index[i]
                })

        return swing_lows

    async def get_smc_signal(self, df, asset='DEFAULT'):
        """Generate combined SMC + Market Sentiment trading signal asynchronously"""
        try:
            market_structure = self.identify_market_structure(df)

            if not market_structure:
                return None

            # Initialize buy and sell scores from market structure
            buy_score = 0
            sell_score = 0

            if market_structure['trend'] == 'BULLISH':
                buy_score += 3
            elif market_structure['trend'] == 'BEARISH':
                sell_score += 3

            if market_structure['bos_detected']:
                if market_structure['trend'] == 'BULLISH':
                    buy_score += 4
                else:
                    sell_score += 4

            # Get market sentiment asynchronously
            sentiment = await self.sentiment_analyzer.get_market_sentiment(asset)

            # Adjust scores with sentiment influence
            if sentiment:
                sentiment_score = sentiment.get('sentiment_score', 50)
                sentiment_trend = sentiment.get('overall_sentiment', 'NEUTRAL')

                # Boost buy_score if sentiment bullish, sell_score if bearish
                if sentiment_trend == 'BULLISH':
                    buy_score += sentiment_score / 20  # scale factor (max +5)
                elif sentiment_trend == 'BEARISH':
                    sell_score += (100 - sentiment_score) / 20  # scale factor (max +5)

            # Calculate total scores and confidence
            total_score = buy_score + sell_score
            if total_score == 0:
                return None

            # Determine final signal and confidence
            if buy_score > sell_score and buy_score >= 3:
                confidence = min((buy_score / total_score) * 100, 99)
                return {
                    'signal_type': 'BUY',
                    'confidence': round(confidence, 1),
                    'market_structure': market_structure,
                    'market_sentiment': sentiment
                }
            elif sell_score > buy_score and sell_score >= 3:
                confidence = min((sell_score / total_score) * 100, 99)
                return {
                    'signal_type': 'SELL',
                    'confidence': round(confidence, 1),
                    'market_structure': market_structure,
                    'market_sentiment': sentiment
                }

            return None

        except Exception as e:
            logging.error(f"Error generating combined SMC signal: {e}")
            return None
