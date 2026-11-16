import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'studyflow-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "database", "studyflow.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {
        'title': 'StudyFlow API',
        'uiversion': 3,
        'description': 'API RESTful para Gestão Acadêmica e Produtividade Estudantil - StudyFlow',
        'version': '1.0.0',
        'termsOfService': '',
        'contact': {
            'name': 'StudyFlow Dev Team',
            'email': 'contato@studyflow.edu'
        },
        'specs_route': '/apidocs/'
    }
