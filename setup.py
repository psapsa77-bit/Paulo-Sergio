"""
Setup script para Labor Termination Analyzer.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lê o README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Lê requirements
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').splitlines()
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="labor-termination-analyzer",
    version="2.0.0",
    author="Labor Termination Analyzer Team",
    author_email="",
    description="Analisador completo de rescisões trabalhistas brasileiras",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/labor-termination-analyzer",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'labor_termination_analyzer': [
            'templates/*.html',
            'templates/*.css',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: Portuguese (Brazilian)",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'rescisao=labor_termination_analyzer.cli:main_cli',
        ],
    },
    extras_require={
        'ocr': [
            'pytesseract>=0.3.10',
            'pdf2image>=1.16.3',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
        ],
    },
    keywords=[
        'rescisao',
        'trabalhista',
        'CLT',
        'labor',
        'termination',
        'HR',
        'RH',
        'recursos humanos',
        'direito trabalhista',
    ],
)
