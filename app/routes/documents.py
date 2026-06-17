import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.document import Document
from app.models.tag import Tag
from app.models.user import User
from app.extensions import db
from app.forms import DocumentForm, DocumentEditForm, SearchForm
from app.utils.decorators import admin_required
from app.utils.audit import register_audit, register_search, get_client_ip
from sqlalchemy import func
from sqlalchemy.orm import subqueryload

documents_bp = Blueprint('documents', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@documents_bp.route('/', methods=['GET', 'POST'])
@login_required
def list_documents():
    form = SearchForm()

    offices = [(0, 'Todas las oficinas')]
    from app.models.office import Office
    for o in Office.query.filter_by(is_active=True).order_by(Office.name).all():
        offices.append((o.id, o.name))

    tags = [(0, 'Todas las etiquetas')]
    for t in Tag.query.order_by(Tag.name).all():
        tags.append((t.id, t.name))

    form.office_id.choices = offices
    form.tag_id.choices = tags

    query = Document.query.options(subqueryload(Document.tags)).filter_by(is_hidden=False)

    if not current_user.is_admin():
        query = query.filter_by(office_id=current_user.office_id)

    search_performed = False
    search_query = ''
    filters = {}

    if form.validate_on_submit():
        search_query = form.query.data or ''
        tag_id = form.tag_id.data or 0
        office_id = form.office_id.data or 0
        date_from = form.date_from.data or ''
        date_to = form.date_to.data or ''
    elif request.args:
        search_query = request.args.get('query', '')
        tag_id = request.args.get('tag_id', 0, type=int)
        office_id = request.args.get('office_id', 0, type=int)
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
    else:
        tag_id = 0
        office_id = 0
        date_from = ''
        date_to = ''

    if search_query:
        search_performed = True
        filters['query'] = search_query
        like_pattern = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Document.title.ilike(like_pattern),
                Document.description.ilike(like_pattern),
                Document.original_filename.ilike(like_pattern)
            )
        )

    if tag_id and tag_id > 0:
        search_performed = True
        filters['tag_id'] = tag_id
        query = query.filter(Document.tags.any(id=tag_id))

    if office_id and office_id > 0:
        if current_user.is_admin():
            search_performed = True
            filters['office_id'] = office_id
            query = query.filter_by(office_id=office_id)

    if date_from:
        search_performed = True
        filters['date_from'] = date_from
        from datetime import datetime
        try:
            dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Document.created_at >= dt)
        except ValueError:
            pass

    if date_to:
        search_performed = True
        filters['date_to'] = date_to
        from datetime import datetime
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Document.created_at <= dt)
        except ValueError:
            pass

    sort = request.args.get('sort', '-created_at')
    if sort == 'title':
        query = query.order_by(Document.title.asc())
    elif sort == '-title':
        query = query.order_by(Document.title.desc())
    elif sort == 'created_at':
        query = query.order_by(Document.created_at.asc())
    elif sort == 'file_size':
        query = query.order_by(Document.file_size.asc())
    elif sort == '-file_size':
        query = query.order_by(Document.file_size.desc())
    else:
        query = query.order_by(Document.created_at.desc())

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    documents = pagination.items

    if search_performed:
        register_search(
            user_id=current_user.id,
            query=search_query,
            filters=filters,
            results_count=pagination.total
        )

    return render_template('documents/list.html',
                         documents=documents,
                         pagination=pagination,
                         form=form,
                         search_query=search_query)


@documents_bp.route('/subir', methods=['GET', 'POST'])
@login_required
def upload():
    form = DocumentForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                flash('El archivo supera el tamaño máximo permitido de 5MB.', 'danger')
                return render_template('documents/upload.html', form=form)

            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, unique_name)
            file.save(filepath)

            document = Document(
                title=form.title.data,
                description=form.description.data or '',
                filename=unique_name,
                original_filename=secure_filename(file.filename),
                file_size=file_size,
                user_id=current_user.id,
                office_id=current_user.office_id
            )
            db.session.add(document)
            db.session.flush()

            tags_str = form.tags.data
            if tags_str:
                for tag_name in [t.strip() for t in tags_str.split(',') if t.strip()]:
                    tag = Tag.query.filter(func.lower(Tag.name) == func.lower(tag_name)).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        db.session.flush()
                    document.tags.append(tag)

            db.session.commit()

            register_audit(
                user_id=current_user.id,
                action='CREATE',
                entity_type='DOCUMENT',
                entity_id=document.id,
                description=f'Documento subido: {document.title}',
                ip_address=get_client_ip(request)
            )

            flash('Documento subido correctamente.', 'success')
            return redirect(url_for('documents.view', document_id=document.id))
        else:
            flash('Tipo de archivo no permitido. Solo PDF.', 'danger')

    return render_template('documents/upload.html', form=form)


@documents_bp.route('/<int:document_id>')
@login_required
def view(document_id):
    document = Document.query.get_or_404(document_id)

    if document.is_hidden and not current_user.is_admin():
        abort(404)

    if not current_user.is_admin() and document.office_id != current_user.office_id:
        abort(403)

    register_audit(
        user_id=current_user.id,
        action='VIEW',
        entity_type='DOCUMENT',
        entity_id=document.id,
        description=f'Visualización: {document.title}',
        ip_address=get_client_ip(request)
    )

    return render_template('documents/view.html', document=document)


@documents_bp.route('/<int:document_id>/editar', methods=['GET', 'POST'])
@login_required
def edit(document_id):
    document = Document.query.get_or_404(document_id)

    if document.is_hidden and not current_user.is_admin():
        abort(404)

    if not current_user.is_admin() and document.user_id != current_user.id:
        flash('No tiene permisos para editar este documento.', 'danger')
        return redirect(url_for('documents.list_documents'))

    form = DocumentEditForm(obj=document)
    form.tags.data = ', '.join([t.name for t in document.tags])

    if form.validate_on_submit():
        document.title = form.title.data
        document.description = form.description.data

        document.tags = []
        tags_str = form.tags.data
        if tags_str:
            for tag_name in [t.strip() for t in tags_str.split(',') if t.strip()]:
                tag = Tag.query.filter(func.lower(Tag.name) == func.lower(tag_name)).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                    db.session.flush()
                document.tags.append(tag)

        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='UPDATE',
            entity_type='DOCUMENT',
            entity_id=document.id,
            description=f'Documento actualizado: {document.title}',
            ip_address=get_client_ip(request)
        )

        flash('Documento actualizado correctamente.', 'success')
        return redirect(url_for('documents.view', document_id=document.id))

    return render_template('documents/edit.html', form=form, document=document)


@documents_bp.route('/<int:document_id>/ocultar', methods=['POST'])
@login_required
@admin_required
def hide(document_id):
    document = Document.query.get_or_404(document_id)

    if document.is_hidden:
        flash('El documento ya está oculto.', 'warning')
    else:
        document.is_hidden = True
        document.hidden_by = current_user.id
        from datetime import datetime
        document.hidden_at = datetime.utcnow()
        document.hidden_reason = request.form.get('reason', 'Ocultado por administrador')
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='HIDE',
            entity_type='DOCUMENT',
            entity_id=document.id,
            description=f'Documento ocultado: {document.title}. Razón: {document.hidden_reason}',
            ip_address=get_client_ip(request)
        )

        flash('Documento ocultado correctamente.', 'success')

    return redirect(url_for('documents.list_documents'))


@documents_bp.route('/<int:document_id>/mostrar', methods=['POST'])
@login_required
@admin_required
def show(document_id):
    document = Document.query.get_or_404(document_id)

    if not document.is_hidden:
        flash('El documento ya está visible.', 'warning')
    else:
        document.is_hidden = False
        document.hidden_by = None
        document.hidden_at = None
        document.hidden_reason = None
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='SHOW',
            entity_type='DOCUMENT',
            entity_id=document.id,
            description=f'Documento restaurado: {document.title}',
            ip_address=get_client_ip(request)
        )

        flash('Documento restaurado correctamente.', 'success')

    return redirect(url_for('documents.list_documents'))


@documents_bp.route('/<int:document_id>/descargar')
@login_required
def download(document_id):
    document = Document.query.get_or_404(document_id)

    if document.is_hidden and not current_user.is_admin():
        abort(404)

    if not current_user.is_admin() and document.office_id != current_user.office_id:
        abort(403)

    register_audit(
        user_id=current_user.id,
        action='DOWNLOAD',
        entity_type='DOCUMENT',
        entity_id=document.id,
        description=f'Descarga: {document.title}',
        ip_address=get_client_ip(request)
    )

    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(
        upload_folder,
        document.filename,
        download_name=document.original_filename,
        as_attachment=True
    )


@documents_bp.route('/<int:document_id>/previsualizar')
@login_required
def preview(document_id):
    document = Document.query.get_or_404(document_id)

    if document.is_hidden and not current_user.is_admin():
        abort(404)

    if not current_user.is_admin() and document.office_id != current_user.office_id:
        abort(403)

    register_audit(
        user_id=current_user.id,
        action='PREVIEW',
        entity_type='DOCUMENT',
        entity_id=document.id,
        description=f'Previsualización: {document.title}',
        ip_address=get_client_ip(request)
    )

    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, document.filename)
