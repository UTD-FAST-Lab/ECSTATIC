from setuptools import setup

setup(
    name='checkmate',
    entry_points={
        'console_script': [
            'checkmate = checkmate.__main__:main'
            ],
        }
    )
