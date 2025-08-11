from flask import render_template, jsonify, request
from app import app, db
from models import TradingSignal, PerformanceMetrics
from quotex_signal_generator import QuotexSignalGenerator
from datetime import datetime, timedelta
import logging

signal_gen = QuotexSignalGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals/current')
def get_current_signals():
    """Get currently active signals"""
    try:
        active_signals = TradingSignal.query.filter_by(is_active=True).order_by(TradingSignal.created_at.desc()).limit(10).all()
        return jsonify({
            'success': True,
            'signals': [signal.to_dict() for signal in active_signals]
        })
    except Exception as e:
        logging.error(f"Error fetching current signals: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch current signals'
        }), 500

@app.route('/api/signals/history')
def get_signal_history():
    """Get signal history with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        asset_filter = request.args.get('asset', None)
        
        query = TradingSignal.query
        if asset_filter:
            query = query.filter_by(asset=asset_filter)
        
        signals = query.order_by(TradingSignal.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'signals': [signal.to_dict() for signal in signals.items],
            'pagination': {
                'page': page,
                'pages': signals.pages,
                'per_page': per_page,
                'total': signals.total
            }
        })
    except Exception as e:
        logging.error(f"Error fetching signal history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch signal history'
        }), 500

@app.route('/api/signals/generate', methods=['POST'])
def generate_signal():
    """Generate a new trading signal"""
    try:
        data = request.get_json()
        asset = data.get('asset', 'EUR/USD')
        
        # Generate signal using the Quotex signal generator
        signal_data = signal_gen.generate_quotex_signal(asset)
        
        if signal_data:
            # Create new signal in database
            signal = TradingSignal()
            signal.asset = signal_data['asset']
            signal.signal_type = signal_data['signal_type']
            signal.entry_price = signal_data['entry_price']
            signal.expiry_time = signal_data['expiry_time']
            signal.confidence = signal_data['confidence']
            db.session.add(signal)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'signal': signal.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to generate signal at this time'
            }), 400
            
    except Exception as e:
        logging.error(f"Error generating signal: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate signal'
        }), 500

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    try:
        metrics = PerformanceMetrics.get_current_metrics()
        metrics.update_metrics()
        
        return jsonify({
            'success': True,
            'metrics': {
                'total_signals': metrics.total_signals,
                'winning_signals': metrics.winning_signals,
                'losing_signals': metrics.losing_signals,
                'win_rate': round(metrics.win_rate, 2),
                'total_profit': round(metrics.total_profit, 2),
                'updated_at': metrics.updated_at.isoformat()
            }
        })
    except Exception as e:
        logging.error(f"Error fetching performance: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch performance metrics'
        }), 500

@app.route('/api/assets')
def get_assets():
    """Get available trading assets categorized by type"""
    try:
        available_assets = signal_gen.get_quotex_assets_by_category()
        
        # Flatten all assets for the main dropdown
        all_assets = []
        for category in available_assets.values():
            all_assets.extend(category)
        
        return jsonify({
            'success': True,
            'assets': all_assets,
            'categories': available_assets
        })
    except Exception as e:
        logging.error(f"Error fetching assets: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch available assets'
        }), 500
