from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.tag import Tag
from app.extensions import db
from app.forms import TagForm
from app.utils.decorators import admin_required
from app.utils.audit import register_audit, get_client_ip
from sqlalchemy import func

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('/')
@login_required
def list_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags/list.html', tags=tags)


@tags_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = Tag.query.filter(func.lower(Tag.name) == func.lower(name)).first()
        if existing:
            flash('Ya existe una etiqueta con ese nombre.', 'danger')
            return render_template('tags/form.html', form=form, title='Crear Etiqueta')

        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='CREATE',
            entity_type='TAG',
            entity_id=tag.id,
            description=f'Etiqueta creada: {tag.name}',
            ip_address=get_client_ip(request)
        )

        flash('Etiqueta creada correctamente.', 'success')
        return redirect(url_for('tags.list_tags'))

    return render_template('tags/form.html', form=form, title='Crear Etiqueta')


@tags_bp.route('/<int:tag_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(obj=tag)

    if form.validate_on_submit():
        name = form.name.data.strip()
        if func.lower(name) != func.lower(tag.name):
            existing = Tag.query.filter(func.lower(Tag.name) == func.lower(name)).first()
            if existing:
                flash('Ya existe una etiqueta con ese nombre.', 'danger')
                return render_template('tags/form.html', form=form, title='Editar Etiqueta', tag=tag)

        tag.name = name
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='UPDATE',
            entity_type='TAG',
            entity_id=tag.id,
            description=f'Etiqueta actualizada: {tag.name}',
            ip_address=get_client_ip(request)
        )

        flash('Etiqueta actualizada correctamente.', 'success')
        return redirect(url_for('tags.list_tags'))

    return render_template('tags/form.html', form=form, title='Editar Etiqueta', tag=tag)


@tags_bp.route('/<int:tag_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    register_audit(
        user_id=current_user.id,
        action='DELETE',
        entity_type='TAG',
        entity_id=tag.id,
        description=f'Etiqueta eliminada: {tag.name}',
        ip_address=get_client_ip(request)
    )

    db.session.delete(tag)
    db.session.commit()

    flash('Etiqueta eliminada correctamente.', 'success')
    return redirect(url_for('tags.list_tags'))
