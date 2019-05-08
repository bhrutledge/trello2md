import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='trello2md',
    version='0.1.2',
    description='Transform Trello card JSON to Markdown',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/bhrutledge/trello2md',
    author='Brian Rutledge',
    author_email='brian@bhrutledge.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    py_modules=['trello2md'],
    entry_points={
        'console_scripts': [
            'trello2md=trello2md:main',
        ],
    },
)
