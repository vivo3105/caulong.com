from flask import render_template, request
from app.blueprints.brands import brands_bp
from app.models import Brand, Racket


@brands_bp.route('/thuong-hieu')
def list_brands():
    brands = Brand.query.order_by(Brand.name).all()
    return render_template('brands/list.html', brands=brands)


@brands_bp.route('/thuong-hieu/<slug>')
def brand_detail(slug):
    brand = Brand.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Racket.query.filter_by(brand_id=brand.id).order_by(
        Racket.view_count.desc()).paginate(page=page, per_page=12, error_out=False)
    rackets = pagination.items
    return render_template('brands/detail.html',
                           brand=brand,
                           rackets=rackets,
                           pagination=pagination)
