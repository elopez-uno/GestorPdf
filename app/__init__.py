from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager
from zoneinfo import ZoneInfo


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.documents import documents_bp
    from app.routes.tags import tags_bp
    from app.routes.offices import offices_bp
    from app.routes.users import users_bp
    from app.routes.audit import audit_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(documents_bp, url_prefix='/documentos')
    app.register_blueprint(tags_bp, url_prefix='/etiquetas')
    app.register_blueprint(offices_bp, url_prefix='/oficinas')
    app.register_blueprint(users_bp, url_prefix='/usuarios')
    app.register_blueprint(audit_bp, url_prefix='/auditoria')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.now(ZoneInfo('America/Argentina/Buenos_Aires'))}

    @app.template_filter('localtime')
    def localtime_filter(dt):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo('America/Argentina/Buenos_Aires'))

    @app.template_filter('datefmt')
    def datefmt_filter(dt, fmt='%d/%m/%Y %H:%M'):
        if dt is None:
            return ''
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        dt = dt.astimezone(ZoneInfo('America/Argentina/Buenos_Aires'))
        return dt.strftime(fmt)

    @app.cli.command('init-data')
    def init_data():
        from app.models.user import User
        from app.models.office import Office
        from app.models.document import Document
        from app.models.tag import Tag, document_tags
        from app.models.audit import AuditLog, SearchLog

        db.create_all()

        if User.query.filter_by(username='admin').first():
            print('El usuario admin ya existe.')
            return

        admin_office = Office.query.filter_by(name='Dirección General').first()
        if not admin_office:
            admin_office = Office(name='Dirección General', description='Oficina administrativa principal')
            db.session.add(admin_office)
            db.session.flush()

        admin = User(
            username='admin',
            email='admin@gestorpdf.com',
            full_name='Administrador del Sistema',
            role='admin',
            office_id=admin_office.id,
            is_active=True
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print('Usuario admin creado exitosamente.')
        print('  Usuario: admin')
        print('  Contraseña: admin')

    return app
