from app.extensions import db
from app.models.audit import AuditLog, SearchLog
from datetime import datetime


def register_audit(user_id, action, entity_type, entity_id=None, description=None, ip_address=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()


def register_search(user_id, query, filters=None, results_count=0):
    log = SearchLog(
        user_id=user_id,
        search_query=query,
        filters=filters,
        results_count=results_count
    )
    db.session.add(log)
    db.session.commit()


def get_client_ip(request):
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr
