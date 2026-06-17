from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.document import Document
from app.models.tag import Tag
from app.models.office import Office
from app.models.user import User
from app.models.audit import AuditLog
from app.extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    total_tags = Tag.query.count()

    if current_user.is_admin():
        total_documents = Document.query.filter_by(is_hidden=False).count()
        total_offices = Office.query.filter_by(is_active=True).count()
        total_users = User.query.filter_by(is_active=True).count()
        recent_documents = Document.query.filter_by(is_hidden=False)\
            .order_by(Document.created_at.desc()).limit(5).all()
        recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(5).all()
        docs_by_office = db.session.query(
            Office.name, func.count(Document.id)
        ).join(Document, Document.office_id == Office.id, isouter=True)\
         .filter(Document.is_hidden == False)\
         .group_by(Office.name).all()
    else:
        office_filter = Document.office_id == current_user.office_id
        total_documents = Document.query.filter_by(is_hidden=False).filter(office_filter).count()
        total_offices = 0
        total_users = 0
        recent_documents = Document.query.filter_by(
            is_hidden=False, office_id=current_user.office_id
        ).order_by(Document.created_at.desc()).limit(5).all()
        recent_audits = AuditLog.query.filter_by(user_id=current_user.id)\
            .order_by(AuditLog.created_at.desc()).limit(5).all()
        docs_by_office = []

    return render_template('dashboard/index.html',
                         total_documents=total_documents,
                         total_tags=total_tags,
                         total_offices=total_offices,
                         total_users=total_users,
                         recent_documents=recent_documents,
                         recent_audits=recent_audits,
                         docs_by_office=docs_by_office)
