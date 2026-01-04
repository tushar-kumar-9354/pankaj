from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BlogPost, BlogSubscriber

@receiver(post_save, sender=BlogPost)
def send_blog_notifications(sender, instance, created, **kwargs):
    """
    Send email notifications to subscribers when a new blog post is published.
    """
    if created and instance.is_published:
        # Get all active and verified subscribers
        subscribers = BlogSubscriber.objects.filter(is_active=True, is_verified=True)
        
        for subscriber in subscribers:
            # Send notification email
            subscriber.send_new_blog_notification(instance)