from django.db import migrations
from django.utils.text import slugify
import uuid

def fix_slugs(apps, schema_editor):
    BlogPost = apps.get_model('pankaj', 'BlogPost')
    
    for post in BlogPost.objects.all():
        # Check if slug is invalid
        if not post.slug or str(post.slug).strip() == '':
            # Generate new slug
            if post.title and post.title.strip() != '':
                base_slug = slugify(post.title)
            else:
                base_slug = f"blog-post-{post.id}"
            
            if not base_slug or base_slug.strip() == '':
                base_slug = f"blog-post-{post.id}"
            
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(id=post.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            post.slug = slug
            post.save(update_fields=['slug'])

class Migration(migrations.Migration):
    dependencies = [
        ('pankaj', '0001_initial'),  # This should be your new initial migration
    ]

    operations = [
        migrations.RunPython(fix_slugs),
    ]