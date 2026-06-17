from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.models.office import Office
from app.extensions import db
from app.forms import UserForm
from app.utils.decorators import admin_required
from app.utils.audit import register_audit, get_client_ip

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.full_name).all()
    return render_template('users/list.html', users=users)


@users_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = UserForm()
    form.office_id.choices = [(0, 'Sin oficina')] + [
        (o.id, o.name) for o in Office.query.filter_by(is_active=True).order_by(Office.name).all()
    ]

    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash('Ya existe un usuario con ese nombre.', 'danger')
            return render_template('users/form.html', form=form, title='Crear Usuario')

        if not form.password.data:
            flash('La contraseña es obligatoria.', 'danger')
            return render_template('users/form.html', form=form, title='Crear Usuario')

        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            role=form.role.data,
            office_id=form.office_id.data if form.office_id.data and form.office_id.data > 0 else None,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='CREATE',
            entity_type='USER',
            entity_id=user.id,
            description=f'Usuario creado: {user.username}',
            ip_address=get_client_ip(request)
        )

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html', form=form, title='Crear Usuario')


@users_bp.route('/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.office_id.choices = [(0, 'Sin oficina')] + [
        (o.id, o.name) for o in Office.query.filter_by(is_active=True).order_by(Office.name).all()
    ]
    form.password.validators = []
    form.password.flags.required = False

    if request.method == 'GET':
        form.office_id.data = user.office_id or 0

    if form.validate_on_submit():
        if form.username.data != user.username:
            existing = User.query.filter_by(username=form.username.data).first()
            if existing:
                flash('Ya existe un usuario con ese nombre.', 'danger')
                return render_template('users/form.html', form=form, title='Editar Usuario', user=user)

        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.role = form.role.data
        user.office_id = form.office_id.data if form.office_id.data and form.office_id.data > 0 else None
        user.is_active = form.is_active.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='UPDATE',
            entity_type='USER',
            entity_id=user.id,
            description=f'Usuario actualizado: {user.username}',
            ip_address=get_client_ip(request)
        )

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html', form=form, title='Editar Usuario', user=user)


@users_bp.route('/<int:user_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    if user_id == current_user.id:
        flash('No puede eliminarse a sí mismo.', 'danger')
        return redirect(url_for('users.list_users'))

    user = User.query.get_or_404(user_id)

    register_audit(
        user_id=current_user.id,
        action='DELETE',
        entity_type='USER',
        entity_id=user.id,
        description=f'Usuario eliminado: {user.username}',
        ip_address=get_client_ip(request)
    )

    user.is_active = False
    db.session.commit()

    flash('Usuario desactivado correctamente.', 'success')
    return redirect(url_for('users.list_users'))
