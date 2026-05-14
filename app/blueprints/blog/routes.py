from flask import render_template, request
from app.blueprints.blog import blog_bp
from app.models import BlogPost


@blog_bp.route('/tin-tuc')
def list_posts():
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query.filter_by(is_published=True).order_by(
        BlogPost.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    posts = pagination.items
    return render_template('blog/list.html', posts=posts, pagination=pagination)


@blog_bp.route('/tin-tuc/<slug>')
def post_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    post.increment_view()

    recent_posts = BlogPost.query.filter(
        BlogPost.is_published == True,
        BlogPost.id != post.id
    ).order_by(BlogPost.created_at.desc()).limit(5).all()

    return render_template('blog/detail.html', post=post, recent_posts=recent_posts)
