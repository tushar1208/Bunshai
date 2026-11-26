"""Weekly auto-rotating SEO/AEO blog engine for BunShai TECHNOHUB.

Rotates featured spotlight and trending article order deterministically every
Monday (ISO week) so search engines and returning visitors see fresh weekly
editions without breaking permanent /blog/<slug>/ URLs.
"""

from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from .blog_data import INITIAL_BLOG_POSTS, WEEKLY_THEMES
from .models import BlogPost


def ensure_blog_seeded():
    """Populate BlogPost table with SEO pillar articles if empty."""
    try:
        if BlogPost.objects.exists():
            return
        today = timezone.localdate()
        objs = []
        for idx, item in enumerate(INITIAL_BLOG_POSTS):
            # Stagger initial publish dates gently across recent days
            pub_date = today - timedelta(days=idx)
            objs.append(
                BlogPost(
                    title=item['title'],
                    slug=item['slug'],
                    category=item['category'],
                    excerpt=item['excerpt'],
                    content_sections=item['content_sections'],
                    faqs=item['faqs'],
                    cover_image=item['cover_image'],
                    primary_keyword=item['primary_keyword'],
                    meta_title=item['meta_title'],
                    meta_description=item['meta_description'],
                    tags=item['tags'],
                    author_name=item['author_name'],
                    author_role=item['author_role'],
                    reading_time=item['reading_time'],
                    related_service_slug=item['related_service_slug'],
                    related_course_slug=item['related_course_slug'],
                    rotation_order=item.get('rotation_order', idx + 1),
                    is_published=True,
                    publish_date=pub_date,
                )
            )
        BlogPost.objects.bulk_create(objs, ignore_conflicts=True)
    except Exception:  # noqa: BLE001 - safe before migrations run
        pass


def get_week_context(today=None):
    """Compute ISO-week rotation metadata, edition countdown, and weekly theme."""
    ref_date = today or timezone.localdate()
    iso_year, iso_week, iso_weekday = ref_date.isocalendar()
    week_start = ref_date - timedelta(days=iso_weekday - 1)
    week_end = week_start + timedelta(days=6)
    next_refresh = week_start + timedelta(days=7)
    days_until_refresh = max(1, (next_refresh - ref_date).days)
    week_index = iso_year * 53 + iso_week
    theme = WEEKLY_THEMES[week_index % len(WEEKLY_THEMES)]

    return {
        'iso_year': iso_year,
        'iso_week': iso_week,
        'week_index': week_index,
        'week_start': week_start,
        'week_end': week_end,
        'next_refresh_date': next_refresh,
        'days_until_refresh': days_until_refresh,
        'theme': theme,
    }


def _rotate_for_week(posts_list, week_index):
    """Rotate ordered posts cleanly so each week promotes a fresh spotlight."""
    n = len(posts_list)
    if n <= 1:
        return list(posts_list)
    offset = week_index % n
    return posts_list[offset:] + posts_list[:offset]


def get_weekly_blog_feed(today=None, category=None, query=None):
    """Return weekly-rotated blog posts, spotlight, category counts, and metadata."""
    ensure_blog_seeded()
    ref_date = today or timezone.localdate()
    week_info = get_week_context(ref_date)

    try:
        base_qs = BlogPost.objects.filter(
            is_published=True,
            publish_date__lte=ref_date,
        ).order_by('rotation_order', '-publish_date', '-id')
        all_posts = list(base_qs)
    except Exception:  # noqa: BLE001
        all_posts = []

    rotated_all = _rotate_for_week(all_posts, week_info['week_index'])
    featured_post = rotated_all[0] if rotated_all else None
    trending_posts = rotated_all[:3]

    # Category counts across all published posts
    cat_counts = {}
    for post in rotated_all:
        cat_counts[post.category] = cat_counts.get(post.category, 0) + 1
    categories = [{'name': k, 'count': v} for k, v in sorted(cat_counts.items())]

    # Apply optional filters while preserving rotated weekly order
    filtered = rotated_all
    if category and category.lower() != 'all':
        filtered = [p for p in filtered if p.category.lower() == category.lower()]
    if query:
        q = query.strip().lower()
        filtered = [
            p for p in filtered
            if (
                q in p.title.lower()
                or q in p.excerpt.lower()
                or q in p.tags.lower()
                or q in p.primary_keyword.lower()
                or q in p.category.lower()
            )
        ]

    return {
        'featured_post': featured_post,
        'posts': filtered,
        'all_posts': rotated_all,
        'trending_posts': trending_posts,
        'categories': categories,
        'week_info': week_info,
        'total_count': len(rotated_all),
    }
