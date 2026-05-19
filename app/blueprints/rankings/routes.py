from flask import render_template, request
from app.blueprints.rankings import rankings_bp
from app.models import RankingWeek, RankingEntry
from app.extensions import db
from sqlalchemy import func


CATEGORIES = {
    'ms': 'Đơn Nam',
    'md': 'Đôi Nam',
    'ws': 'Đơn Nữ',
    'wd': 'Đôi Nữ',
}


@rankings_bp.route('/')
def index():
    category = request.args.get('cat', 'ms')
    if category not in CATEGORIES:
        category = 'ms'
    week_id = request.args.get('week', type=int)
    country_filter = request.args.get('country', '').strip()
    vietnam_only = request.args.get('vn') == '1'

    weeks = RankingWeek.query.order_by(RankingWeek.week_date.desc()).all()

    if week_id:
        selected_week = RankingWeek.query.get(week_id)
    else:
        selected_week = RankingWeek.query.order_by(RankingWeek.week_date.desc()).first()

    entries = []
    countries = []
    if selected_week:
        q = RankingEntry.query.filter_by(week_id=selected_week.id, category=category)

        if vietnam_only:
            q = q.filter(
                db.or_(
                    func.lower(RankingEntry.country).contains('vietnam'),
                    func.lower(RankingEntry.country_code) == 'vn',
                    func.lower(RankingEntry.country_code) == 'vie',
                )
            )
        elif country_filter:
            q = q.filter(
                db.or_(
                    func.lower(RankingEntry.country).contains(country_filter.lower()),
                    func.lower(RankingEntry.country_code).contains(country_filter.lower()),
                )
            )

        entries = q.order_by(RankingEntry.rank).all()

        countries = db.session.query(
            RankingEntry.country, RankingEntry.country_code
        ).filter_by(
            week_id=selected_week.id, category=category
        ).distinct().order_by(RankingEntry.country).all()

    return render_template(
        'rankings/index.html',
        weeks=weeks,
        selected_week=selected_week,
        entries=entries,
        category=category,
        categories=CATEGORIES,
        countries=countries,
        country_filter=country_filter,
        vietnam_only=vietnam_only,
    )
