from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.office import Office
from app.extensions import db
from app.forms import OfficeForm
from app.utils.decorators import admin_required
from app.utils.audit import register_audit, get_client_ip

offices_bp = Blueprint('offices', __name__)


@offices_bp.route('/')
@login_required
@admin_required
def list_offices():
    offices = Office.query.order_by(Office.name).all()
    return render_template('offices/list.html', offices=offices)


@offices_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = OfficeForm()
    if form.validate_on_submit():
        existing = Office.query.filter_by(name=form.name.data).first()
        if existing:
            flash('Ya existe una oficina con ese nombre.', 'danger')
            return render_template('offices/form.html', form=form, title='Crear Oficina')

        office = Office(
            name=form.name.data,
            description=form.description.data or ''
        )
        db.session.add(office)
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='CREATE',
            entity_type='OFFICE',
            entity_id=office.id,
            description=f'Oficina creada: {office.name}',
            ip_address=get_client_ip(request)
        )

        flash('Oficina creada correctamente.', 'success')
        return redirect(url_for('offices.list_offices'))

    return render_template('offices/form.html', form=form, title='Crear Oficina')


@offices_bp.route('/<int:office_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(office_id):
    office = Office.query.get_or_404(office_id)
    form = OfficeForm(obj=office)

    if form.validate_on_submit():
        if form.name.data != office.name:
            existing = Office.query.filter_by(name=form.name.data).first()
            if existing:
                flash('Ya existe una oficina con ese nombre.', 'danger')
                return render_template('offices/form.html', form=form, title='Editar Oficina', office=office)

        office.name = form.name.data
        office.description = form.description.data
        office.is_active = form.is_active.data
        db.session.commit()

        register_audit(
            user_id=current_user.id,
            action='UPDATE',
            entity_type='OFFICE',
            entity_id=office.id,
            description=f'Oficina actualizada: {office.name}',
            ip_address=get_client_ip(request)
        )

        flash('Oficina actualizada correctamente.', 'success')
        return redirect(url_for('offices.list_offices'))

    return render_template('offices/form.html', form=form, title='Editar Oficina', office=office)
