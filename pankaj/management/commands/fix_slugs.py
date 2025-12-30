# pankaj/management/commands/fix_slugs.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from pankaj.models import BlogPost

class Command(BaseCommand):
    help = 'Fix all blog posts with empty or invalid slugs'

    def handle(self, *args, **options):
        # Get all blog posts
        all_posts = BlogPost.objects.all()
        
        fixed_count = 0
        for post in all_posts:
            original_slug = post.slug
            needs_fix = False
            
            # Check if slug is empty or contains only whitespace
            if not post.slug or str(post.slug).strip() == '':
                needs_fix = True
                self.stdout.write(f"Post '{post.title}' has empty slug")
            
            # Generate new slug if needed
            if needs_fix:
                # Generate base slug from title
                if post.title:
                    base_slug = slugify(post.title)
                else:
                    base_slug = f"blog-post-{post.id}"
                
                # Ensure base slug is not empty
                if not base_slug or base_slug.strip() == '':
                    base_slug = f"blog-post-{post.id}"
                
                # Make slug unique
                slug = base_slug
                counter = 1
                while BlogPost.objects.filter(slug=slug).exclude(id=post.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                # Update the slug
                post.slug = slug
                post.save(update_fields=['slug'])
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Fixed slug for '{post.title}': {original_slug} → {slug}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Successfully fixed {fixed_count} blog post(s)")
        )