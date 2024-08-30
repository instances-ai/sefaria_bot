from setuptools import setup, find_packages

setup(
    name='sefaria_bot',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit==1.38.0',
        'dotenv',
        'openai',
        'requests',
        'beautifulsoup4',   # This is the package for BeautifulSoup
        'regex',            # This package provides a regex module that supersedes the built-in `re` module
        'unicodedata2',     # A better version of Python's unicodedata module
        'uuid'              # Although uuid is part of Python's standard library, including for completeness
    ],
    python_requires='>=3.7',  # Streamlit/other dependencies might require a newer Python version
    entry_points={
        'console_scripts': [
            'your_project=your_project.module:main',
        ],
    },
)

