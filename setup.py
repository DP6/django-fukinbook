from setuptools import setup

setup(
    name='django-fukinbook',
    version='0.3.0',
    description="Easy django app to use facebook with async requests",
    author='Binarios Inglorios',
    author_email='binarios.inglorios@digitalcube.com.br',
    url='',
    license='GPL',
    packages=['django_fukinbook'],
    package_data={'django_fukinbook': ['templates/*']},

    zip_safe=False,
    install_requires=[
        'simplejson',
        'django',
        'tornado',
	'httplib2',
    ],
)
