from app import db
from datetime import datetime
from sqlalchemy import func

class TradingSignal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(20), nullable=False)
    signal_type = db.Column(db.String(10), nullable=False)  # 'BUY' or 'SELL'
    entry_price = db.Column(db.Float, nullable=False)
    expiry_time = db.Column(db.Integer, nullable=False)  # in minutes
    confidence = db.Column(db.Float, nullable=False)  # 0-100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    result = db.Column(db.String(10))  # 'WIN', 'LOSS', or None
    profit_loss = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset': self.asset,
            'signal_type': self.signal_type,
            'entry_price': self.entry_price,
            'expiry_time': self.expiry_time,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'result': self.result,
            'profit_loss': self.profit_loss
        }

class PerformanceMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_signals = db.Column(db.Integer, default=0)
    winning_signals = db.Column(db.Integer, default=0)
    losing_signals = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    total_profit = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_current_metrics():
        metrics = PerformanceMetrics.query.first()
        if not metrics:
            metrics = PerformanceMetrics()
            db.session.add(metrics)
            db.session.commit()
        return metrics
    
    def update_metrics(self):
        # Calculate metrics from actual signal results
        completed_signals = TradingSignal.query.filter(TradingSignal.result.isnot(None)).all()
        
        self.total_signals = len(completed_signals)
        self.winning_signals = len([s for s in completed_signals if s.result == 'WIN'])
        self.losing_signals = len([s for s in completed_signals if s.result == 'LOSS'])
        self.win_rate = (self.winning_signals / self.total_signals * 100) if self.total_signals > 0 else 0
        self.total_profit = sum([s.profit_loss for s in completed_signals])
        self.updated_at = datetime.utcnow()
        
        db.session.commit()
