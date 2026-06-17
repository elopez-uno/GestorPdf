from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.tag import Tag
from app.models.office import Office
from app.models.document import Document
from app.models.audit import AuditLog, SearchLog
from app.models.user import User
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats')
@login_required
def stats():
    total_docs = Document.query.filter_by(is_hidden=False).count()
    total_tags = Tag.query.count()
    total_offices = Office.query.filter_by(is_active=True).count()
    total_users = User.query.filter_by(is_active=True).count()

    return jsonify({
        'documents': total_docs,
        'tags': total_tags,
        'offices': total_offices,
        'users': total_users
    })


@api_bp.route('/tags')
@login_required
def tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([{'id': t.id, 'name': t.name, 'count': t.documents.filter(Document.is_hidden == False).count()} for t in tags])


@api_bp.route('/offices')
@login_required
def offices():
    offices = Office.query.filter_by(is_active=True).order_by(Office.name).all()
    return jsonify([{'id': o.id, 'name': o.name} for o in offices])


@api_bp.route('/charts/documents-by-office')
@login_required
def documents_by_office():
    data = db.session.query(
        Office.name,
        func.count(Document.id)
    ).join(Document, Document.office_id == Office.id, isouter=True)\
     .filter(Document.is_hidden == False)\
     .group_by(Office.name).all()

    return jsonify({
        'labels': [d[0] for d in data],
        'values': [d[1] for d in data]
    })


@api_bp.route('/charts/documents-by-month')
@login_required
def documents_by_month():
    six_months_ago = datetime.utcnow() - timedelta(days=180)

    data = db.session.query(
        func.date_trunc('month', Document.created_at).label('month'),
        func.count(Document.id)
    ).filter(
        Document.is_hidden == False,
        Document.created_at >= six_months_ago
    ).group_by('month').order_by('month').all()

    months = []
    counts = []
    for d in data:
        months.append(d.month.strftime('%b %Y'))
        counts.append(d.count)

    return jsonify({'labels': months, 'values': counts})
