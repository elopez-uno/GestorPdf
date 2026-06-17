from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.forms import LoginForm, ChangePasswordForm
from app.utils.audit import register_audit, get_client_ip

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Su cuenta está desactivada. Contacte al administrador.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user)
            register_audit(
                user_id=user.id,
                action='LOGIN',
                entity_type='USER',
                entity_id=user.id,
                description=f'Inicio de sesión: {user.username}',
                ip_address=get_client_ip(request)
            )

            next_page = request.args.get('next')
            flash(f'Bienvenido, {user.full_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    register_audit(
        user_id=current_user.id,
        action='LOGOUT',
        entity_type='USER',
        entity_id=current_user.id,
        description=f'Cierre de sesión: {current_user.username}',
        ip_address=get_client_ip(request)
    )
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('auth/change_password.html', form=form)

        if form.new_password.data != form.confirm_password.data:
            flash('Las contraseñas nuevas no coinciden.', 'danger')
            return render_template('auth/change_password.html', form=form)

        current_user.set_password(form.new_password.data)
        from app.extensions import db
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='CHANGE_PASSWORD',
            entity_type='USER',
            entity_id=current_user.id,
            description='Cambio de contraseña',
            ip_address=get_client_ip(request)
        )

        flash('Contraseña actualizada correctamente.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html', form=form)
