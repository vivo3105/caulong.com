# CầuLong.com

Vietnamese badminton racket catalog and review platform built with Flask.

## Setup

```bash
pip install -r requirements.txt
python seed.py
python run.py
```

## Access

- **Website**: http://localhost:5000
- **Admin**: http://localhost:5000/admin
  - Username: `admin`
  - Password: `admin123`

## Features

- Racket catalog with filtering (brand, weight, balance, flexibility, skill level, price)
- Side-by-side racket comparison (up to 3)
- Brand pages
- Blog / news articles
- AJAX instant search
- Dark mode toggle
- Admin CRUD for rackets, brands, blog posts
- Image upload with Pillow compression
- SEO: sitemap.xml, robots.txt, Open Graph tags
- Vietnamese UI throughout
