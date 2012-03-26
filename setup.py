from setuptools import setup

setup(
    name = 'django-fukinbook',
    version = '0.1',
    description = "Easy django app to use facebook",
    author = 'Binarios Inglorios',
    author_email = 'binarios.inglorios@digitalcube.com.br',
    url = '',
    license = 'GPL',
    packages = ['django_fukinbook'],
    zip_safe=False,
    install_requires=[
        'simplejson',
        'django',
    ],
)
