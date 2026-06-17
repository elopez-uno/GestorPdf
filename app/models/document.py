from app.extensions import db
from datetime import datetime


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(300), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False, default='application/pdf')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'), nullable=True)
    is_hidden = db.Column(db.Boolean, default=False)
    hidden_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    hidden_at = db.Column(db.DateTime, nullable=True)
    hidden_reason = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    office = db.relationship('Office', backref='documents', lazy=True)
    hider = db.relationship('User', backref='hidden_documents', lazy=True,
                             foreign_keys=[hidden_by])

    def __repr__(self):
        return f'<Document {self.title}>'
