from flask import render_template, request, jsonify, Response, current_app, send_from_directory
from app.blueprints.main import main_bp
from app.models import Racket, Brand, BlogPost, RacketImage, RankingWeek
from app.extensions import db
from sqlalchemy import func
from datetime import datetime
import os


@main_bp.route('/media/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files from UPLOAD_FOLDER (works on both local and Azure)."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main_bp.route('/')
def index():
    featured_rackets = Racket.query.filter_by(is_featured=True).order_by(
        Racket.view_count.desc()).limit(6).all()
    if len(featured_rackets) < 6:
        extra = Racket.query.filter_by(is_featured=False).order_by(
            Racket.view_count.desc()).limit(6 - len(featured_rackets)).all()
        featured_rackets.extend(extra)

    brands = Brand.query.order_by(Brand.name).all()
    latest_posts = BlogPost.query.filter_by(is_published=True).order_by(
        BlogPost.created_at.desc()).limit(3).all()

    return render_template('main/index.html',
                           featured_rackets=featured_rackets,
                           brands=brands,
                           latest_posts=latest_posts)


@main_bp.route('/suggest')
def suggest():
    q = request.args.get('q', '').strip()
    if len(q) < 1:
        return jsonify([])
    q_lower = q.lower()
    full = func.lower(Brand.name) + ' ' + func.lower(Racket.name)
    rackets = Racket.query.join(Brand).filter(
        db.or_(
            func.lower(Racket.name).contains(q_lower),
            func.lower(Brand.name).contains(q_lower),
            full.contains(q_lower)
        )
    ).order_by(Racket.name).limit(8).all()
    return jsonify([
        {'name': r.name, 'brand': r.brand.name, 'slug': r.slug}
        for r in rackets
    ])


@main_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.args.get('format') == 'json'

    results = []
    if query:
        q_lower = query.lower()
        full = func.lower(Brand.name) + ' ' + func.lower(Racket.name)
        rackets = Racket.query.join(Brand).filter(
            db.or_(
                func.lower(Racket.name).contains(q_lower),
                func.lower(Brand.name).contains(q_lower),
                full.contains(q_lower),
                func.lower(Racket.description).contains(q_lower)
            )
        ).limit(20).all()

        for r in rackets:
            primary = r.primary_image
            image_url = f'/media/{primary.filename}' if primary else '/static/img/placeholder.png'
            results.append({
                'name': r.name,
                'slug': r.slug,
                'brand': r.brand.name,
                'image_url': image_url,
                'price': r.price,
                'skill_level': r.skill_level_display
            })

    if is_ajax:
        return jsonify(results)

    return render_template('main/search.html', query=query, results=results)


@main_bp.route('/so-sanh')
def compare():
    ids = request.args.getlist('id')
    rackets = []
    if ids:
        for rid in ids[:3]:
            try:
                r = Racket.query.get(int(rid))
                if r:
                    rackets.append(r)
            except (ValueError, TypeError):
                pass

    return render_template('rackets/compare.html', rackets=rackets)


@main_bp.route('/sitemap.xml')
def sitemap():
    pages = []
    base_url = request.host_url.rstrip('/').replace('http://', 'https://')
    today = datetime.utcnow().strftime('%Y-%m-%d')

    # Static pages
    pages.append({'loc': base_url + '/', 'lastmod': today, 'priority': '1.0', 'changefreq': 'daily'})
    pages.append({'loc': base_url + '/bang-xep-hang', 'lastmod': today, 'priority': '0.9', 'changefreq': 'weekly'})
    pages.append({'loc': base_url + '/vot-cau-long', 'lastmod': today, 'priority': '0.9', 'changefreq': 'daily'})
    pages.append({'loc': base_url + '/thuong-hieu', 'lastmod': today, 'priority': '0.8', 'changefreq': 'weekly'})
    pages.append({'loc': base_url + '/tin-tuc', 'lastmod': today, 'priority': '0.8', 'changefreq': 'daily'})

    # Rankings per category
    ranking_cats = [('ms', 'Đơn Nam'), ('md', 'Đôi Nam'), ('ws', 'Đơn Nữ'), ('wd', 'Đôi Nữ'), ('xd', 'Đôi Nam Nữ')]
    for cat, _ in ranking_cats:
        pages.append({'loc': f'{base_url}/bang-xep-hang?cat={cat}', 'lastmod': today, 'priority': '0.8', 'changefreq': 'weekly'})

    # Rackets
    rackets = Racket.query.filter_by().order_by(Racket.updated_at.desc()).all()
    for r in rackets:
        pages.append({
            'loc': f'{base_url}/vot-cau-long/{r.slug}',
            'lastmod': r.updated_at.strftime('%Y-%m-%d'),
            'priority': '0.8',
            'changefreq': 'weekly'
        })

    # Brands
    brands = Brand.query.order_by(Brand.name).all()
    for b in brands:
        pages.append({
            'loc': f'{base_url}/thuong-hieu/{b.slug}',
            'lastmod': today,
            'priority': '0.7',
            'changefreq': 'weekly'
        })

    # Blog posts
    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.updated_at.desc()).all()
    for p in posts:
        pages.append({
            'loc': f'{base_url}/tin-tuc/{p.slug}',
            'lastmod': p.updated_at.strftime('%Y-%m-%d'),
            'priority': '0.6',
            'changefreq': 'monthly'
        })

    xml = render_template('sitemap.xml', pages=pages)
    return Response(xml, mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    base_url = request.host_url.rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /dang-nhap
Disallow: /search?
Disallow: /so-sanh
Crawl-delay: 1

User-agent: Googlebot
Allow: /
Disallow: /admin/
Disallow: /dang-nhap

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')
