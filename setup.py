import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='RighiDiary',
    author='Vadym Teliatnyk',
    author_email='laivhakin@gmail.com',
    description='Obtaining data from the electronic diary of the lyceum "Liceo Scientifico A. Righi"',
    keywords='example, pypi, package, righi, righiAPI, register, diary',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Komo4ekoI/RighiRegisterAPI',
    project_urls={
        'Documentation': 'https://github.com/Komo4ekoI/RighiRegisterAPI',
        'Bug Reports':
        'https://github.com/Komo4ekoI/RighiRegisterAPI/issues',
        'Source Code': 'https://github.com/Komo4ekoI/RighiRegisterAPI',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # https://pypi.org/classifiers/
        'Development Status :: 1 - Planning',

        'Intended Audience :: Developers',
        'Topic :: Communications',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=['aiohttp>=3.8.5', 'beautifulsoup4>=4.12.2'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
)
