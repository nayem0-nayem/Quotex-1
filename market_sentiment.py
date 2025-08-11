import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time

class MarketSentimentAnalyzer:
    """Real-time market sentiment and fundamental analysis"""
    
    def __init__(self):
        self.sentiment_sources = {
            'fear_greed': 'https://api.alternative.me/fng/',
        }
        
    def get_fear_greed_index(self):
        """Get Fear & Greed Index for market sentiment"""
        try:
            response = requests.get(self.sentiment_sources['fear_greed'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    return {
                        'value': int(data['data'][0]['value']),
                        'classification': data['data'][0]['value_classification'],
                        'timestamp': data['data'][0]['timestamp']
                    }
        except Exception as e:
            logging.error(f"Error fetching Fear & Greed Index: {e}")
        
        return None
    
    def get_market_sentiment(self, asset):
        """Get comprehensive market sentiment for an asset"""
        try:
            sentiment = {
                'overall_sentiment': 'NEUTRAL',
                'sentiment_score': 50,
                'fear_greed': None,
                'risk_sentiment': 'NEUTRAL'
            }
            
            # Get Fear & Greed Index
            fear_greed = self.get_fear_greed_index()
            if fear_greed:
                sentiment['fear_greed'] = fear_greed
                
                # Adjust sentiment score based on Fear & Greed
                if fear_greed['classification'] == 'Extreme Fear':
                    sentiment['sentiment_score'] = 20
                    sentiment['overall_sentiment'] = 'BEARISH'
                elif fear_greed['classification'] == 'Fear':
                    sentiment['sentiment_score'] = 35
                    sentiment['overall_sentiment'] = 'BEARISH'
                elif fear_greed['classification'] == 'Greed':
                    sentiment['sentiment_score'] = 65
                    sentiment['overall_sentiment'] = 'BULLISH'
                elif fear_greed['classification'] == 'Extreme Greed':
                    sentiment['sentiment_score'] = 80
                    sentiment['overall_sentiment'] = 'BULLISH'
            
            # Ensure sentiment score is within bounds
            sentiment['sentiment_score'] = max(0, min(100, sentiment['sentiment_score']))
            
            # Final sentiment classification
            if sentiment['sentiment_score'] < 30:
                sentiment['overall_sentiment'] = 'BEARISH'
            elif sentiment['sentiment_score'] > 70:
                sentiment['overall_sentiment'] = 'BULLISH'
            else:
                sentiment['overall_sentiment'] = 'NEUTRAL'
            
            return sentiment
            
        except Exception as e:
            logging.error(f"Error getting market sentiment: {e}")
            return None
