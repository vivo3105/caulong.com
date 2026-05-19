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
from app.models import Racket, Brand, BlogPost, Review, User, RacketImage, generate_slug, RankingWeek, RankingEntry, RANKING_CATEGORIES
from app.extensions import db, csrf

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
            has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
            if has_alpha:
                img = img.convert('RGBA')
                save_ext = 'png'
                unique_name = unique_name.rsplit('.', 1)[0] + '.png'
                filepath = os.path.join(upload_folder, unique_name)
            else:
                img = img.convert('RGB')
                save_ext = ext
            max_width = 800
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            if save_ext == 'png':
                img.save(filepath, optimize=True)
            else:
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
    no_image = request.args.get('no_image', '')
    brand_id = request.args.get('brand_id', '', type=str)
    query = Racket.query.join(Brand)
    if search:
        query = query.filter(
            db.or_(Racket.name.ilike(f'%{search}%'), Brand.name.ilike(f'%{search}%'))
        )
    if no_image:
        query = query.filter(~Racket.images.any())
    if brand_id:
        query = query.filter(Racket.brand_id == int(brand_id))
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Racket.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    brands = Brand.query.order_by(Brand.name).all()
    return render_template('admin/rackets/list.html', pagination=pagination,
                           rackets=pagination.items, search=search, no_image=no_image,
                           brands=brands, brand_id=brand_id)


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
            weight_class=','.join(request.form.getlist('weight_class')) or None,
            grip_sizes=','.join(request.form.getlist('grip_sizes')) or None,
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
        racket.weight_class = ','.join(request.form.getlist('weight_class')) or None
        racket.grip_sizes = ','.join(request.form.getlist('grip_sizes')) or None
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


@admin_bp.route('/rackets/images/<int:image_id>/xoa', methods=['POST'])
@csrf.exempt
@admin_required
def racket_image_delete(image_id):
    img = RacketImage.query.get_or_404(image_id)
    racket_id = img.racket_id
    was_primary = img.is_primary

    # Delete file from disk
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass

    db.session.delete(img)
    db.session.flush()

    # Reassign primary to first remaining image
    if was_primary:
        first = RacketImage.query.filter_by(racket_id=racket_id).order_by(RacketImage.order).first()
        if first:
            first.is_primary = True

    db.session.commit()
    return jsonify({'ok': True})


@admin_bp.route('/rackets/images/<int:image_id>/set-primary', methods=['POST'])
@csrf.exempt
@admin_required
def racket_image_set_primary(image_id):
    img = RacketImage.query.get_or_404(image_id)
    RacketImage.query.filter_by(racket_id=img.racket_id).update({'is_primary': False})
    img.is_primary = True
    db.session.commit()
    return jsonify({'ok': True})


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
    'name', 'brand', 'weight_class', 'grip_sizes', 'balance_type', 'flexibility',
    'frame_material', 'shaft_material', 'skill_level', 'price',
    'string_tension_min', 'string_tension_max', 'length_mm',
    'description', 'pros', 'cons', 'playing_style',
    'is_featured', 'meta_title', 'meta_description',
]

BOOL_FIELDS = {'is_featured'}
INT_FIELDS = {'price', 'string_tension_min', 'string_tension_max', 'length_mm'}

PLAYING_STYLE_MAP = {
    'tấn công': 'attack',
    'phòng thủ': 'defense',
    'toàn diện': 'allround',
    'tốc độ':   'speed',
    'điều cầu': 'control',
    # also accept English keys directly
    'attack': 'attack', 'defense': 'defense', 'allround': 'allround',
    'speed': 'speed', 'control': 'control',
}
PLAYING_STYLE_DISPLAY = {
    'attack': 'Tấn công', 'defense': 'Phòng thủ', 'allround': 'Toàn diện',
    'speed': 'Tốc độ', 'control': 'Điều cầu',
}


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
        elif field == 'playing_style':
            data[field] = PLAYING_STYLE_MAP.get(str(val).strip().lower(), val)
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
    'name', 'brand', 'weight_class', 'grip_sizes', 'balance_type', 'flexibility',
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
        'grip_sizes': r.grip_sizes or '',
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
        'playing_style': PLAYING_STYLE_DISPLAY.get(r.playing_style or '', r.playing_style or ''),
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


# ── Rankings management ────────────────────────────────────────────────────────

@admin_bp.route('/bang-xep-hang')
@admin_required
def rankings_list():
    weeks = RankingWeek.query.order_by(RankingWeek.week_date.desc()).all()
    week_counts = {}
    for week in weeks:
        week_counts[week.id] = {
            cat: RankingEntry.query.filter_by(week_id=week.id, category=cat).count()
            for cat in RANKING_CATEGORIES
        }
    return render_template('admin/rankings/index.html', weeks=weeks, week_counts=week_counts)


@admin_bp.route('/bang-xep-hang/them', methods=['GET', 'POST'])
@admin_required
def rankings_week_add():
    if request.method == 'POST':
        from datetime import date as date_type
        week_date_str = request.form.get('week_date', '').strip()
        if not week_date_str:
            flash('Ngày không được để trống.', 'error')
            return redirect(url_for('admin.rankings_week_add'))
        try:
            week_date = date_type.fromisoformat(week_date_str)
        except ValueError:
            flash('Ngày không hợp lệ.', 'error')
            return redirect(url_for('admin.rankings_week_add'))
        if RankingWeek.query.filter_by(week_date=week_date).first():
            flash('Tuần này đã tồn tại.', 'error')
            return redirect(url_for('admin.rankings_week_add'))
        is_current = bool(request.form.get('is_current'))
        if is_current:
            RankingWeek.query.update({'is_current': False})
        week = RankingWeek(
            week_date=week_date,
            label=request.form.get('label', '').strip() or None,
            is_current=is_current,
        )
        db.session.add(week)
        db.session.commit()
        flash(f'Đã thêm tuần {week.display_label}.', 'success')
        return redirect(url_for('admin.rankings_list'))
    return render_template('admin/rankings/week_form.html', week=None)


@admin_bp.route('/bang-xep-hang/<int:id>/sua', methods=['GET', 'POST'])
@admin_required
def rankings_week_edit(id):
    week = RankingWeek.query.get_or_404(id)
    if request.method == 'POST':
        from datetime import date as date_type
        week_date_str = request.form.get('week_date', '').strip()
        try:
            week_date = date_type.fromisoformat(week_date_str)
        except ValueError:
            flash('Ngày không hợp lệ.', 'error')
            return redirect(url_for('admin.rankings_week_edit', id=id))
        existing = RankingWeek.query.filter_by(week_date=week_date).first()
        if existing and existing.id != id:
            flash('Tuần này đã tồn tại.', 'error')
            return redirect(url_for('admin.rankings_week_edit', id=id))
        is_current = bool(request.form.get('is_current'))
        if is_current:
            RankingWeek.query.filter(RankingWeek.id != id).update({'is_current': False})
        week.week_date = week_date
        week.label = request.form.get('label', '').strip() or None
        week.is_current = is_current
        db.session.commit()
        flash('Đã cập nhật.', 'success')
        return redirect(url_for('admin.rankings_list'))
    return render_template('admin/rankings/week_form.html', week=week)


@admin_bp.route('/bang-xep-hang/<int:id>/xoa', methods=['POST'])
@admin_required
def rankings_week_delete(id):
    week = RankingWeek.query.get_or_404(id)
    label = week.display_label
    db.session.delete(week)
    db.session.commit()
    flash(f'Đã xóa tuần {label}.', 'success')
    return redirect(url_for('admin.rankings_list'))


@admin_bp.route('/bang-xep-hang/<int:week_id>/nhap/<category>', methods=['GET'])
@admin_required
def rankings_entries(week_id, category):
    if category not in RANKING_CATEGORIES:
        flash('Danh mục không hợp lệ.', 'error')
        return redirect(url_for('admin.rankings_list'))
    week = RankingWeek.query.get_or_404(week_id)
    entries = RankingEntry.query.filter_by(week_id=week_id, category=category).order_by(RankingEntry.rank).all()
    return render_template('admin/rankings/entries.html',
                           week=week, category=category,
                           categories=RANKING_CATEGORIES, entries=entries)


@admin_bp.route('/bang-xep-hang/<int:week_id>/nhap/<category>/import', methods=['POST'])
@admin_required
def rankings_entries_import(week_id, category):
    if category not in RANKING_CATEGORIES:
        flash('Danh mục không hợp lệ.', 'error')
        return redirect(url_for('admin.rankings_list'))
    RankingWeek.query.get_or_404(week_id)
    bulk_data = request.form.get('bulk_data', '').strip()
    if not bulk_data:
        flash('Không có dữ liệu.', 'error')
        return redirect(url_for('admin.rankings_entries', week_id=week_id, category=category))

    RankingEntry.query.filter_by(week_id=week_id, category=category).delete()

    entries_to_add, errors = _parse_bwf_or_custom(bulk_data, category)

    for e in entries_to_add:
        e.week_id = week_id
        db.session.add(e)
    db.session.commit()

    if errors:
        flash(f'Nhập {len(entries_to_add)} bản ghi. Lỗi: {"; ".join(errors[:3])}',
              'warning' if entries_to_add else 'error')
    else:
        flash(f'Đã nhập {len(entries_to_add)} bản ghi cho {RANKING_CATEGORIES[category]}.', 'success')
    return redirect(url_for('admin.rankings_entries', week_id=week_id, category=category))


# Country name → ISO alpha-2 code for common badminton nations
_COUNTRY_CODES = {
    'china': 'CN', 'thailand': 'TH', 'denmark': 'DK', 'france': 'FR',
    'indonesia': 'ID', 'malaysia': 'MY', 'japan': 'JP', 'south korea': 'KR',
    'korea': 'KR', 'india': 'IN', 'taiwan': 'TW', 'chinese taipei': 'TW',
    'germany': 'DE', 'spain': 'ES', 'england': 'GB', 'scotland': 'GB',
    'australia': 'AU', 'canada': 'CA', 'hong kong': 'HK', 'hong kong china': 'HK',
    'singapore': 'SG', 'vietnam': 'VN', 'viet nam': 'VN',
    'netherlands': 'NL', 'sweden': 'SE', 'norway': 'NO', 'finland': 'FI',
    'russia': 'RU', 'ukraine': 'UA', 'poland': 'PL', 'switzerland': 'CH',
    'brazil': 'BR', 'mexico': 'MX', 'united states': 'US', 'usa': 'US',
    'new zealand': 'NZ', 'sri lanka': 'LK', 'pakistan': 'PK',
    'mauritius': 'MU', 'peru': 'PE', 'portugal': 'PT', 'italy': 'IT',
    'nigeria': 'NG', 'egypt': 'EG', 'south africa': 'ZA',
    'cambodia': 'KH', 'myanmar': 'MM', 'philippines': 'PH', 'thailand': 'TH',
}


def _country_code(name: str) -> str:
    return _COUNTRY_CODES.get(name.lower().strip(), '')


def _parse_movement(raw: str, rank: int):
    """Return previous_rank from BWF movement string like '-', '▲2', '▼3', 'NEW'."""
    raw = raw.strip()
    if raw in ('-', '=', ''):
        return rank
    if raw.upper() == 'NEW':
        return None
    # Arrow characters: ▲ ▼ or plain +/-
    import re
    m = re.match(r'[▲+](\d+)', raw)
    if m:
        return rank + int(m.group(1))
    m = re.match(r'[▼-](\d+)', raw)
    if m:
        return max(1, rank - int(m.group(1)))
    return None


def _parse_points(raw: str) -> float:
    """Parse '108,905' or '108905' or '108.905' → float."""
    return float(raw.replace(',', '').replace(' ', '')) if raw.strip() else 0.0


def _is_bwf_format(lines: list) -> bool:
    """Detect BWF copy-paste format: header row OR pattern rank/movement/name/nation/stats."""
    if not lines:
        return False
    if lines[0].upper().startswith('RANK'):
        return True
    # Check if first non-empty line is a pure integer (rank)
    for line in lines[:3]:
        stripped = line.strip()
        if stripped and stripped.isdigit():
            return True
    return False


def _parse_bwf_or_custom(bulk_data: str, category: str):
    """Parse data and return (list[RankingEntry], list[error_strings])."""
    is_doubles = category in ('md', 'wd')
    lines = bulk_data.splitlines()
    non_empty = [l for l in lines if l.strip()]

    if _is_bwf_format(non_empty):
        return _parse_bwf_format(non_empty, category, is_doubles)
    return _parse_custom_format(non_empty, category, is_doubles)


def _parse_bwf_format(lines: list, category: str, is_doubles: bool):
    """
    BWF copy-paste format (5 lines per player for singles, 6 for doubles):
      rank
      movement  (-  /  ▲N  /  ▼N  /  NEW)
      player name  [for doubles: also next line is partner name]
      nation
      tournaments<TAB>points[<TAB>breakdown]
    Header row 'RANK NAME …' is skipped automatically.
    """
    entries, errors = [], []

    # Strip header
    start = 0
    if lines and lines[0].strip().upper().startswith('RANK'):
        start = 1

    lines = lines[start:]
    i = 0
    lines_per = 6 if is_doubles else 5

    while i < len(lines):
        chunk = lines[i:i + lines_per]
        # Skip blank chunks
        if not any(l.strip() for l in chunk):
            i += 1
            continue

        try:
            rank_str = chunk[0].strip()
            if not rank_str.isdigit():
                i += 1
                continue

            rank = int(rank_str)
            movement_raw = chunk[1].strip() if len(chunk) > 1 else '-'
            prev_rank = _parse_movement(movement_raw, rank)

            if is_doubles:
                player1 = chunk[2].strip() if len(chunk) > 2 else ''
                player2 = chunk[3].strip() if len(chunk) > 3 else ''
                nation_line = chunk[4].strip() if len(chunk) > 4 else ''
                stats_line = chunk[5].strip() if len(chunk) > 5 else ''
            else:
                player1 = chunk[2].strip() if len(chunk) > 2 else ''
                player2 = ''
                nation_line = chunk[3].strip() if len(chunk) > 3 else ''
                stats_line = chunk[4].strip() if len(chunk) > 4 else ''

            # Stats line: "12\t108,905\t" → tournaments, points
            stat_parts = [p.strip() for p in stats_line.split('\t')]
            tournaments = int(stat_parts[0]) if stat_parts and stat_parts[0].isdigit() else 0
            points_raw = stat_parts[1] if len(stat_parts) > 1 else '0'
            points = _parse_points(points_raw)

            code = _country_code(nation_line)

            entries.append(RankingEntry(
                category=category,
                rank=rank,
                player_name=player1,
                player_name_2=player2 or None,
                country=nation_line,
                country_code=code or None,
                points=points,
                tournaments_played=tournaments,
                previous_rank=prev_rank,
            ))
            i += lines_per
        except Exception as e:
            errors.append(f'Nhóm dòng {i + 1}: {e}')
            i += 1

    return entries, errors


def _parse_custom_format(lines: list, category: str, is_doubles: bool):
    """Original tab-separated custom format."""
    entries, errors = [], []
    for idx, line in enumerate(lines, 1):
        parts = [p.strip() for p in line.split('\t')]
        try:
            if is_doubles:
                rank = int(parts[0])
                player1 = parts[1]
                player2 = parts[2] if len(parts) > 2 else ''
                country = parts[3] if len(parts) > 3 else ''
                code = parts[4] if len(parts) > 4 else ''
                points = _parse_points(parts[5]) if len(parts) > 5 and parts[5] else 0
                tournaments = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0
                prev_rank = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None
            else:
                rank = int(parts[0])
                player1 = parts[1]
                player2 = ''
                country = parts[2] if len(parts) > 2 else ''
                code = parts[3] if len(parts) > 3 else ''
                points = _parse_points(parts[4]) if len(parts) > 4 and parts[4] else 0
                tournaments = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
                prev_rank = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None

            entries.append(RankingEntry(
                category=category,
                rank=rank, player_name=player1, player_name_2=player2 or None,
                country=country, country_code=(code.upper() or _country_code(country)) or None,
                points=points, tournaments_played=tournaments,
                previous_rank=prev_rank,
            ))
        except (IndexError, ValueError) as e:
            errors.append(f'Dòng {idx}: {e}')

    return entries, errors


@admin_bp.route('/bang-xep-hang/<int:week_id>/xoa-het/<category>', methods=['POST'])
@admin_required
def rankings_entries_clear(week_id, category):
    RankingWeek.query.get_or_404(week_id)
    RankingEntry.query.filter_by(week_id=week_id, category=category).delete()
    db.session.commit()
    flash(f'Đã xóa toàn bộ {RANKING_CATEGORIES.get(category, category)}.', 'success')
    return redirect(url_for('admin.rankings_entries', week_id=week_id, category=category))


@admin_bp.route('/bang-xep-hang/entry/<int:entry_id>/xoa', methods=['POST'])
@admin_required
def rankings_entry_delete(entry_id):
    entry = RankingEntry.query.get_or_404(entry_id)
    week_id = entry.week_id
    category = entry.category
    db.session.delete(entry)
    db.session.commit()
    flash('Đã xóa bản ghi.', 'success')
    return redirect(url_for('admin.rankings_entries', week_id=week_id, category=category))
