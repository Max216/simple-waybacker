from setuptools import setup

setup(
    name='waybacker',
    version='0.1.0',
    description='Easy wrapper to collect webpages via the wayback machine.',
    url='https://github.com/Max216/simple-waybacker',
    author='Max Glockner',
    author_email='maxg216@gmail.com',
    license='Apache 2.0',
    packages=[
        'waybacker',
        'waybacker.util',
        'waybacker.api',
        'waybacker.components',
        'waybacker.db',
        'waybacker.init'
    ],
    install_requires=[
        "requests~=2.31.0",
        "beautifulsoup4~=4.11.1",
        "tqdm~=4.64.1",
        "pandas~=2.2.0"
    ]
)