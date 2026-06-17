from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models.audit import AuditLog, SearchLog
from app.models.user import User
from app.utils.decorators import admin_required
from app.extensions import db

audit_bp = Blueprint('audit', __name__)


@audit_bp.route('/')
@login_required
@admin_required
def list_audits():
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', 0, type=int)
    action = request.args.get('action', '')
    entity_type = request.args.get('entity_type', '')

    query = AuditLog.query

    if user_id and user_id > 0:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter_by(action=action)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)

    query = query.order_by(AuditLog.created_at.desc())
    pagination = query.paginate(page=page, per_page=30, error_out=False)

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()

    actions = db.session.query(AuditLog.action).distinct().order_by(AuditLog.action).all()
    entity_types = db.session.query(AuditLog.entity_type).distinct().order_by(AuditLog.entity_type).all()

    return render_template('audit/list.html',
                         logs=pagination.items,
                         pagination=pagination,
                         users=users,
                         actions=[a[0] for a in actions],
                         entity_types=[e[0] for e in entity_types],
                         selected_user=user_id,
                         selected_action=action,
                         selected_entity_type=entity_type)


@audit_bp.route('/busquedas')
@login_required
@admin_required
def search_history():
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', 0, type=int)

    query = SearchLog.query

    if user_id and user_id > 0:
        query = query.filter_by(user_id=user_id)

    query = query.order_by(SearchLog.created_at.desc())
    pagination = query.paginate(page=page, per_page=30, error_out=False)

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()

    return render_template('audit/search_history.html',
                         logs=pagination.items,
                         pagination=pagination,
                         users=users,
                         selected_user=user_id)


@audit_bp.route('/usuario/<int:user_id>')
@login_required
@admin_required
def user_audit(user_id):
    user = User.query.get_or_404(user_id)

    page = request.args.get('page', 1, type=int)
    audits = AuditLog.query.filter_by(user_id=user_id)\
        .order_by(AuditLog.created_at.desc())\
        .paginate(page=page, per_page=30, error_out=False)

    searches = SearchLog.query.filter_by(user_id=user_id)\
        .order_by(SearchLog.created_at.desc())\
        .limit(20).all()

    return render_template('audit/user_audit.html',
                         audit_user=user,
                         audits=audits.items,
                         searches=searches,
                         pagination=audits)
