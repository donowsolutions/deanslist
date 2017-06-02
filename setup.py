from setuptools import setup, find_packages

__name__ = 'deanslist'
__version__ = '0.6'

setup(
    name=__name__,
    version=__version__,
    url='https://github.com/donowsolutions/%s' % __name__,
    author='Jonathan Elliott Blum',
    author_email='jon@donowsolutions.com',
    description='DeansList API wrapper',
    license='MIT',
    packages=['deanslist'],
    install_requires=[
        'requests >=2.10.0, <3',
    ],
    keywords=['deanslist', 'api', 'wrapper'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Education'
    ],
)
