from setuptools import setup
import os


PROJECT_ROOT, _ = os.path.split(__file__)
PROJECT_NAME = 'chatbot'
VERSION = '2.5'
PROJECT_AUTHORS = 'lb'
PROJECT_EMAILS = '423497786@qq.com'
PROJECT_URL = 'https://github.com/lb423497786/chatbot-py'
SHORT_DESCRIPTION = (
    'chatbot is a machine learning, conversational dialog engine.'
)


# Get the long description from the relevant file
try:
    DESCRIPTION = open(os.path.join(PROJECT_ROOT, 'README.rst')).read()
except IOError:
    DESCRIPTION = SHORT_DESCRIPTION


REQUIREMENTS = []
with open('requirements.txt') as requirements:
    for requirement in requirements:
            REQUIREMENTS.append(requirement)


setup(
    name=PROJECT_NAME.lower(),
    version=VERSION,
    author=PROJECT_AUTHORS,
    author_email=PROJECT_EMAILS,
    url=PROJECT_URL,
    description=SHORT_DESCRIPTION,
    long_description=DESCRIPTION,
    platforms=['any'],
    keywords=['chatbot'],
    python_requires='>=3.4, <4',
    install_requires=REQUIREMENTS,

    # packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    packages=[
        'chatbot',
        'chatbot.ext',
    ],
    package_dir={'chatbot': 'chatbot'},
    test_suite='tests',
    package_data={
        'chatbot': [
            '*.*',
            'log/*',
            'data/*',
        ],
    }
)
