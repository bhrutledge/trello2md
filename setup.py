import setuptools

setuptools.setup(
    name='trello2md',
    version='0.1.1',
    description='Transform Trello card JSON to Markdown',
    py_modules=['trello2md'],
    entry_points={
        'console_scripts': [
            'trello2md=trello2md:main',
        ],
    },
)
