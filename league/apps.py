from django.apps import AppConfig


class LeagueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'league'

    def ready(self):
        # Import signals here to ensure they are loaded
        import league.signals
