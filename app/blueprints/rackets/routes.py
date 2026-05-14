from flask import render_template, request, abort
from app.blueprints.rackets import rackets_bp
from app.models import Racket, Brand
from app.extensions import db


@rackets_bp.route('/vot-cau-long')
def list_rackets():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Build query
    query = Racket.query.join(Brand)

    # Filters
    brand_slugs = request.args.getlist('brand')
    weight_classes = request.args.getlist('weight_class')
    balance_types = request.args.getlist('balance_type')
    flexibilities = request.args.getlist('flexibility')
    skill_levels = request.args.getlist('skill_level')
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    sort = request.args.get('sort', 'popular')

    if brand_slugs:
        query = query.filter(Brand.slug.in_(brand_slugs))
    if weight_classes:
        query = query.filter(Racket.weight_class.in_(weight_classes))
    if balance_types:
        query = query.filter(Racket.balance_type.in_(balance_types))
    if flexibilities:
        query = query.filter(Racket.flexibility.in_(flexibilities))
    if skill_levels:
        query = query.filter(Racket.skill_level.in_(skill_levels))
    if price_min is not None:
        query = query.filter(Racket.price >= price_min)
    if price_max is not None:
        query = query.filter(Racket.price <= price_max)

    # Sorting
    if sort == 'price_asc':
        query = query.order_by(Racket.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Racket.price.desc())
    elif sort == 'newest':
        query = query.order_by(Racket.created_at.desc())
    elif sort == 'name':
        query = query.order_by(Racket.name.asc())
    else:  # popular
        query = query.order_by(Racket.view_count.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rackets = pagination.items

    all_brands = Brand.query.order_by(Brand.name).all()

    # Active filters for display
    active_filters = []
    if brand_slugs:
        for slug in brand_slugs:
            b = Brand.query.filter_by(slug=slug).first()
            if b:
                active_filters.append({'type': 'brand', 'value': slug, 'label': b.name})
    for wc in weight_classes:
        active_filters.append({'type': 'weight_class', 'value': wc, 'label': wc})
    for bt in balance_types:
        bt_labels = {'head_heavy': 'Nặng đầu', 'even': 'Cân bằng', 'head_light': 'Nhẹ đầu'}
        active_filters.append({'type': 'balance_type', 'value': bt, 'label': bt_labels.get(bt, bt)})
    for fl in flexibilities:
        fl_labels = {'extra_stiff': 'Siêu cứng', 'stiff': 'Cứng', 'medium': 'Trung bình',
                     'flexible': 'Mềm', 'extra_flexible': 'Siêu mềm'}
        active_filters.append({'type': 'flexibility', 'value': fl, 'label': fl_labels.get(fl, fl)})
    for sl in skill_levels:
        sl_labels = {'beginner': 'Người mới', 'intermediate': 'Trung cấp',
                     'advanced': 'Nâng cao', 'professional': 'Chuyên nghiệp'}
        active_filters.append({'type': 'skill_level', 'value': sl, 'label': sl_labels.get(sl, sl)})

    return render_template('rackets/list.html',
                           rackets=rackets,
                           pagination=pagination,
                           all_brands=all_brands,
                           active_filters=active_filters,
                           current_sort=sort,
                           selected_brands=brand_slugs,
                           selected_weight=weight_classes,
                           selected_balance=balance_types,
                           selected_flexibility=flexibilities,
                           selected_skill=skill_levels,
                           price_min=price_min,
                           price_max=price_max)


@rackets_bp.route('/vot-cau-long/<slug>')
def racket_detail(slug):
    racket = Racket.query.filter_by(slug=slug).first_or_404()
    racket.increment_view()

    # Similar rackets (same brand or same skill level)
    similar = Racket.query.filter(
        Racket.id != racket.id,
        db.or_(
            Racket.brand_id == racket.brand_id,
            Racket.skill_level == racket.skill_level
        )
    ).order_by(Racket.view_count.desc()).limit(4).all()

    images = racket.images.order_by('order').all()
    reviews = racket.reviews.order_by('created_at desc').all()

    return render_template('rackets/detail.html',
                           racket=racket,
                           similar_rackets=similar,
                           images=images,
                           reviews=reviews)
