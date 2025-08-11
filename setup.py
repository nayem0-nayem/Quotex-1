import os
import sys
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quotex-signal-bot",
    version="1.0.0",
    author="Quotex Signal Bot",
    author_email="support@quotexsignals.com",
    description="Advanced Quotex Trading Signal Bot with 95%+ accuracy using SMC/ICT analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quotex-signals/quotex-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=3.0.0",
        "Flask-SQLAlchemy>=3.1.1",
        "Flask-CORS>=4.0.0",
        "Werkzeug>=3.0.1",
        "yfinance>=0.2.61",
        "pandas>=2.2.3",
        "numpy>=2.2.6",
        "requests>=2.32.3",
        "beautifulsoup4>=4.13.4",
        "ta>=0.11.0",
        "plotly>=6.1.2",
    ],
    entry_points={
        "console_scripts": [
            "quotex-bot=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.png", "*.ico"],
    },
)
