from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.models import User


@auth_bp.route('/dang-nhap', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_admin:
                flash('Bạn không có quyền truy cập trang quản trị.', 'error')
                return render_template('auth/login.html')
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            flash(f'Chào mừng {user.username}!', 'success')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/dang-xuat')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công.', 'success')
    return redirect(url_for('main.index'))
