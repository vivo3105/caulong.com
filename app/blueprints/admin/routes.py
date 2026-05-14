import os
import csv
import io
import json
from datetime import datetime
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.blueprints.admin import admin_bp
from app.models import Racket, Brand, BlogPost, Review, User, RacketImage, generate_slug
from app.extensions import db

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_image(file, subfolder=''):
    if not file or not allowed_file(file.filename):
        return None
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_folder = os.path.join(upload_folder, subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, unique_name)

    if PIL_AVAILABLE:
        try:
            img = Image.open(file)
            img = img.convert('RGB')
            max_width = 800
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            img.save(filepath, optimize=True, quality=85)
        except Exception:
            file.seek(0)
            file.save(filepath)
    else:
        file.save(filepath)

    return unique_name if not subfolder else f"{subfolder}/{unique_name}"


# ─── Dashboard ───────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def dashboard():
    total_rackets = Racket.query.count()
    total_brands = Brand.query.count()
    total_posts = BlogPost.query.count()
    total_reviews = Review.query.count()
    total_users = User.query.count()

    top_rackets = Racket.query.order_by(Racket.view_count.desc()).limit(10).all()
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           total_rackets=total_rackets,
                           total_brands=total_brands,
                           total_posts=total_posts,
                           total_reviews=total_reviews,
                           total_users=total_users,
                           top_rackets=top_rackets,
                           recent_reviews=recent_reviews)


# ─── Rackets ─────────────────────────────────────────────────────────────────

@admin_bp.route('/rackets')
@admin_required
def rackets_list():
    search = request.args.get('q', '')
    query = Racket.query.join(Brand)
    if search:
        query = query.filter(
            db.or_(Racket.name.ilike(f'%{search}%'), Brand.name.ilike(f'%{search}%'))
        )
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Racket.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/rackets/list.html', pagination=pagination,
                           rackets=pagination.items, search=search)


@admin_bp.route('/rackets/them', methods=['GET', 'POST'])
@admin_required
def racket_add():
    brands = Brand.query.order_by(Brand.name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Tên vợt không được để trống.', 'error')
            return render_template('admin/rackets/form.html', brands=brands, racket=None)

        slug = generate_slug(name)
        # Make slug unique
        base_slug = slug
        counter = 1
        while Racket.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        racket = Racket(
            name=name,
            slug=slug,
            brand_id=request.form.get('brand_id', type=int),
            weight_class=request.form.get('weight_class') or None,
            balance_type=request.form.get('balance_type') or None,
            flexibility=request.form.get('flexibility') or None,
            frame_material=request.form.get('frame_material', '').strip() or None,
            shaft_material=request.form.get('shaft_material', '').strip() or None,
            skill_level=request.form.get('skill_level') or None,
            price=request.form.get('price', type=int),
            description=request.form.get('description', '').strip() or None,
            pros=request.form.get('pros', '').strip() or None,
            cons=request.form.get('cons', '').strip() or None,
            playing_style=request.form.get('playing_style', '').strip() or None,
            string_tension_min=request.form.get('string_tension_min', type=int),
            string_tension_max=request.form.get('string_tension_max', type=int),
            length_mm=request.form.get('length_mm', 675, type=int),
            is_featured=bool(request.form.get('is_featured')),
            meta_title=request.form.get('meta_title', '').strip() or None,
            meta_description=request.form.get('meta_description', '').strip() or None,
        )
        db.session.add(racket)
        db.session.flush()

        # Handle image uploads
        files = request.files.getlist('images')
        first = True
        for f in files:
            if f and f.filename:
                fname = save_image(f)
                if fname:
                    img = RacketImage(racket_id=racket.id, filename=fname,
                                      is_primary=first, order=0 if first else 1)
                    db.session.add(img)
                    first = False

        db.session.commit()
        flash(f'Đã thêm vợt "{name}" thành công!', 'success')
        return redirect(url_for('admin.rackets_list'))

    return render_template('admin/rackets/form.html', brands=brands, racket=None)


@admin_bp.route('/rackets/<int:id>/sua', methods=['GET', 'POST'])
@admin_required
def racket_edit(id):
    racket = Racket.query.get_or_404(id)
    brands = Brand.query.order_by(Brand.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Tên vợt không được để trống.', 'error')
            return render_template('admin/rackets/form.html', brands=brands, racket=racket)

        if name != racket.name:
            slug = generate_slug(name)
            base_slug = slug
            counter = 1
            while Racket.query.filter(Racket.slug == slug, Racket.id != id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            racket.slug = slug

        racket.name = name
        racket.brand_id = request.form.get('brand_id', type=int)
        racket.weight_class = request.form.get('weight_class') or None
        racket.balance_type = request.form.get('balance_type') or None
        racket.flexibility = request.form.get('flexibility') or None
        racket.frame_material = request.form.get('frame_material', '').strip() or None
        racket.shaft_material = request.form.get('shaft_material', '').strip() or None
        racket.skill_level = request.form.get('skill_level') or None
        racket.price = request.form.get('price', type=int)
        racket.description = request.form.get('description', '').strip() or None
        racket.pros = request.form.get('pros', '').strip() or None
        racket.cons = request.form.get('cons', '').strip() or None
        racket.playing_style = request.form.get('playing_style', '').strip() or None
        racket.string_tension_min = request.form.get('string_tension_min', type=int)
        racket.string_tension_max = request.form.get('string_tension_max', type=int)
        racket.length_mm = request.form.get('length_mm', 675, type=int)
        racket.is_featured = bool(request.form.get('is_featured'))
        racket.meta_title = request.form.get('meta_title', '').strip() or None
        racket.meta_description = request.form.get('meta_description', '').strip() or None
        racket.updated_at = datetime.utcnow()

        # Handle new image uploads
        files = request.files.getlist('images')
        has_primary = racket.images.filter_by(is_primary=True).first() is not None
        for f in files:
            if f and f.filename:
                fname = save_image(f)
                if fname:
                    img = RacketImage(racket_id=racket.id, filename=fname,
                                      is_primary=not has_primary, order=1)
                    db.session.add(img)
                    has_primary = True

        db.session.commit()
        flash(f'Đã cập nhật vợt "{name}" thành công!', 'success')
        return redirect(url_for('admin.rackets_list'))

    return render_template('admin/rackets/form.html', brands=brands, racket=racket)


@admin_bp.route('/rackets/<int:id>/xoa', methods=['POST'])
@admin_required
def racket_delete(id):
    racket = Racket.query.get_or_404(id)
    name = racket.name
    db.session.delete(racket)
    db.session.commit()
    flash(f'Đã xóa vợt "{name}".', 'success')
    return redirect(url_for('admin.rackets_list'))


# ─── Brands ──────────────────────────────────────────────────────────────────

@admin_bp.route('/thuong-hieu')
@admin_required
def brands_list():
    brands = Brand.query.order_by(Brand.name).all()
    return render_template('admin/brands/list.html', brands=brands)


@admin_bp.route('/thuong-hieu/them', methods=['GET', 'POST'])
@admin_required
def brand_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Tên thương hiệu không được để trống.', 'error')
            return render_template('admin/brands/form.html', brand=None)

        slug = generate_slug(name)
        base_slug = slug
        counter = 1
        while Brand.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        logo_file = request.files.get('logo')
        logo_fname = save_image(logo_file) if logo_file and logo_file.filename else None

        banner_file = request.files.get('banner_image')
        banner_fname = save_image(banner_file) if banner_file and banner_file.filename else None

        brand = Brand(
            name=name,
            slug=slug,
            description=request.form.get('description', '').strip() or None,
            country=request.form.get('country', '').strip() or None,
            logo=logo_fname,
            banner_image=banner_fname,
        )
        db.session.add(brand)
        db.session.commit()
        flash(f'Đã thêm thương hiệu "{name}" thành công!', 'success')
        return redirect(url_for('admin.brands_list'))

    return render_template('admin/brands/form.html', brand=None)


@admin_bp.route('/thuong-hieu/<int:id>/sua', methods=['GET', 'POST'])
@admin_required
def brand_edit(id):
    brand = Brand.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Tên thương hiệu không được để trống.', 'error')
            return render_template('admin/brands/form.html', brand=brand)

        brand.name = name
        brand.description = request.form.get('description', '').strip() or None
        brand.country = request.form.get('country', '').strip() or None

        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            brand.logo = save_image(logo_file)

        banner_file = request.files.get('banner_image')
        if banner_file and banner_file.filename:
            brand.banner_image = save_image(banner_file)

        db.session.commit()
        flash(f'Đã cập nhật thương hiệu "{name}" thành công!', 'success')
        return redirect(url_for('admin.brands_list'))

    return render_template('admin/brands/form.html', brand=brand)


@admin_bp.route('/thuong-hieu/<int:id>/xoa', methods=['POST'])
@admin_required
def brand_delete(id):
    brand = Brand.query.get_or_404(id)
    name = brand.name
    db.session.delete(brand)
    db.session.commit()
    flash(f'Đã xóa thương hiệu "{name}".', 'success')
    return redirect(url_for('admin.brands_list'))


# ─── Blog ────────────────────────────────────────────────────────────────────

@admin_bp.route('/bai-viet')
@admin_required
def blog_list():
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/blog/list.html', posts=pagination.items, pagination=pagination)


@admin_bp.route('/bai-viet/them', methods=['GET', 'POST'])
@admin_required
def blog_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Tiêu đề bài viết không được để trống.', 'error')
            return render_template('admin/blog/form.html', post=None)

        slug = generate_slug(title)
        base_slug = slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        img_file = request.files.get('featured_image')
        img_fname = save_image(img_file) if img_file and img_file.filename else None

        post = BlogPost(
            title=title,
            slug=slug,
            content=request.form.get('content', ''),
            author_id=current_user.id,
            featured_image=img_fname,
            meta_title=request.form.get('meta_title', '').strip() or None,
            meta_description=request.form.get('meta_description', '').strip() or None,
            is_published=bool(request.form.get('is_published')),
        )
        db.session.add(post)
        db.session.commit()
        flash(f'Đã thêm bài viết "{title}" thành công!', 'success')
        return redirect(url_for('admin.blog_list'))

    return render_template('admin/blog/form.html', post=None)


@admin_bp.route('/bai-viet/<int:id>/sua', methods=['GET', 'POST'])
@admin_required
def blog_edit(id):
    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Tiêu đề bài viết không được để trống.', 'error')
            return render_template('admin/blog/form.html', post=post)

        post.title = title
        post.content = request.form.get('content', '')
        post.meta_title = request.form.get('meta_title', '').strip() or None
        post.meta_description = request.form.get('meta_description', '').strip() or None
        post.is_published = bool(request.form.get('is_published'))
        post.updated_at = datetime.utcnow()

        img_file = request.files.get('featured_image')
        if img_file and img_file.filename:
            post.featured_image = save_image(img_file)

        db.session.commit()
        flash(f'Đã cập nhật bài viết "{title}" thành công!', 'success')
        return redirect(url_for('admin.blog_list'))

    return render_template('admin/blog/form.html', post=post)


@admin_bp.route('/bai-viet/<int:id>/xoa', methods=['POST'])
@admin_required
def blog_delete(id):
    post = BlogPost.query.get_or_404(id)
    title = post.title
    db.session.delete(post)
    db.session.commit()
    flash(f'Đã xóa bài viết "{title}".', 'success')
    return redirect(url_for('admin.blog_list'))


# ─── Image Upload (AJAX) ─────────────────────────────────────────────────────

@admin_bp.route('/upload', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file nào được gửi.'}), 400
    f = request.files['file']
    if not f or not f.filename:
        return jsonify({'error': 'File không hợp lệ.'}), 400
    fname = save_image(f)
    if not fname:
        return jsonify({'error': 'Định dạng file không được hỗ trợ.'}), 400
    return jsonify({'filename': fname, 'url': f'/media/{fname}'})


# ── Bulk Import ───────────────────────────────────────────────────────────────

IMPORT_FIELDS = [
    'name', 'brand', 'weight_class', 'balance_type', 'flexibility',
    'frame_material', 'shaft_material', 'skill_level', 'price',
    'string_tension_min', 'string_tension_max', 'length_mm',
    'description', 'pros', 'cons', 'playing_style',
    'is_featured', 'meta_title', 'meta_description',
]

BOOL_FIELDS = {'is_featured'}
INT_FIELDS = {'price', 'string_tension_min', 'string_tension_max', 'length_mm'}


def _parse_row(row):
    """Normalise a dict row from CSV/JSON into cleaned field values."""
    data = {}
    for field in IMPORT_FIELDS:
        val = row.get(field, '').strip() if isinstance(row.get(field), str) else row.get(field)
        if val is None or val == '':
            continue
        if field in BOOL_FIELDS:
            data[field] = str(val).lower() in ('1', 'true', 'yes', 'có')
        elif field in INT_FIELDS:
            try:
                data[field] = int(val)
            except (ValueError, TypeError):
                pass
        else:
            data[field] = val
    return data


def _apply_row(data, brands_cache):
    """Insert or update a Racket from cleaned data. Returns (action, error)."""
    brand_name = data.pop('brand', None)
    if not brand_name:
        return None, 'Thiếu tên thương hiệu (brand)'
    racket_name = data.get('name')
    if not racket_name:
        return None, 'Thiếu tên vợt (name)'

    # Resolve brand
    brand = brands_cache.get(brand_name.lower())
    if not brand:
        brand = Brand.query.filter(Brand.name.ilike(brand_name)).first()
        if not brand:
            return None, f'Không tìm thấy thương hiệu "{brand_name}"'
        brands_cache[brand_name.lower()] = brand

    slug = generate_slug(racket_name)
    existing = Racket.query.filter(
        db.or_(Racket.slug == slug, Racket.name.ilike(racket_name))
    ).first()

    if existing:
        for k, v in data.items():
            if k != 'name':
                setattr(existing, k, v)
        existing.brand_id = brand.id
        existing.updated_at = datetime.utcnow()
        return 'updated', None
    else:
        racket = Racket(slug=slug, brand_id=brand.id, **data)
        db.session.add(racket)
        return 'created', None


@admin_bp.route('/nhap-lieu-hang-loat', methods=['GET', 'POST'])
@admin_required
def bulk_import():
    brands = Brand.query.order_by(Brand.name).all()
    template_fields = IMPORT_FIELDS

    if request.method == 'GET':
        return render_template('admin/rackets/bulk_import.html',
                               brands=brands,
                               template_fields=template_fields)

    # ── Parse input ──────────────────────────────────────────────────────────
    rows = []
    errors = []
    fmt = request.form.get('format', 'csv')
    raw_text = request.form.get('data', '').strip()
    uploaded = request.files.get('file')

    if uploaded and uploaded.filename:
        raw_bytes = uploaded.read()
        raw_text = raw_bytes.decode('utf-8-sig', errors='replace')
        ext = uploaded.filename.rsplit('.', 1)[-1].lower()
        fmt = 'json' if ext == 'json' else 'csv'

    if not raw_text:
        flash('Vui lòng nhập dữ liệu hoặc tải file lên.', 'error')
        return render_template('admin/rackets/bulk_import.html',
                               brands=brands, template_fields=template_fields)

    if fmt == 'json':
        try:
            payload = json.loads(raw_text)
            rows = payload if isinstance(payload, list) else [payload]
        except json.JSONDecodeError as e:
            flash(f'JSON không hợp lệ: {e}', 'error')
            return render_template('admin/rackets/bulk_import.html',
                                   brands=brands, template_fields=template_fields,
                                   raw_data=raw_text)
    else:
        reader = csv.DictReader(io.StringIO(raw_text))
        rows = list(reader)

    if not rows:
        flash('Không có dữ liệu để nhập.', 'error')
        return render_template('admin/rackets/bulk_import.html',
                               brands=brands, template_fields=template_fields)

    # ── Process rows ─────────────────────────────────────────────────────────
    created = updated = 0
    brands_cache = {}

    for i, row in enumerate(rows, start=1):
        data = _parse_row(row)
        action, err = _apply_row(data, brands_cache)
        if err:
            errors.append(f'Dòng {i} ({row.get("name", "?")}): {err}')
        elif action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi lưu dữ liệu: {e}', 'error')
        return render_template('admin/rackets/bulk_import.html',
                               brands=brands, template_fields=template_fields)

    if created or updated:
        flash(f'Nhập thành công: {created} vợt mới, {updated} vợt đã cập nhật.', 'success')
    if errors:
        for err in errors:
            flash(err, 'error')

    return redirect(url_for('admin.bulk_import'))


# ── Export ────────────────────────────────────────────────────────────────────

EXPORT_FIELDS = [
    'name', 'brand', 'weight_class', 'balance_type', 'flexibility',
    'frame_material', 'shaft_material', 'skill_level', 'price',
    'string_tension_min', 'string_tension_max', 'length_mm',
    'description', 'pros', 'cons', 'playing_style',
    'is_featured', 'meta_title', 'meta_description',
]


def _racket_to_dict(r):
    return {
        'name': r.name,
        'brand': r.brand.name,
        'weight_class': r.weight_class or '',
        'balance_type': r.balance_type or '',
        'flexibility': r.flexibility or '',
        'frame_material': r.frame_material or '',
        'shaft_material': r.shaft_material or '',
        'skill_level': r.skill_level or '',
        'price': r.price or '',
        'string_tension_min': r.string_tension_min or '',
        'string_tension_max': r.string_tension_max or '',
        'length_mm': r.length_mm or '',
        'description': r.description or '',
        'pros': r.pros or '',
        'cons': r.cons or '',
        'playing_style': r.playing_style or '',
        'is_featured': 'true' if r.is_featured else 'false',
        'meta_title': r.meta_title or '',
        'meta_description': r.meta_description or '',
    }


@admin_bp.route('/xuat-du-lieu')
@admin_required
def export_rackets():
    fmt = request.args.get('format', 'csv')
    brand_id = request.args.get('brand_id', type=int)

    query = Racket.query.join(Brand).order_by(Brand.name, Racket.name)
    if brand_id:
        query = query.filter(Racket.brand_id == brand_id)
    rackets = query.all()

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    if fmt == 'json':
        data = [_racket_to_dict(r) for r in rackets]
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return Response(
            content,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=rackets_{timestamp}.json'}
        )

    # CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    for r in rackets:
        writer.writerow(_racket_to_dict(r))

    return Response(
        '﻿' + output.getvalue(),  # BOM for Excel UTF-8 compatibility
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=rackets_{timestamp}.csv'}
    )
