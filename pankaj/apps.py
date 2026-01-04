from django.apps import AppConfig

class PankajConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pankaj'
    
    def ready(self):
        import pankaj.signals