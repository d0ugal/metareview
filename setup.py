from setuptools import setup

setup(
    name="metareview",
    version="0.0.1",
    url="http://",
    license="MIT",
    description="",
    long_description="",
    author="Dougal Matthews",
    author_email="dougal@dougalmatthews.com",
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'metareview = metareview.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
