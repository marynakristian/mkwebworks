# main/context_processors.py

def language_choices(request):
    return {
        'language_choices': [
            {'code': 'en', 'label': 'English'},
            {'code': 'cs', 'label': 'Čeština'},
            {'code': 'ro', 'label': 'Română'},
            {'code': 'uk', 'label': 'Українська'},
            {'code': 'ru', 'label': 'Русский'},
        ]
    }
