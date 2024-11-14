# setup.py
from setuptools import setup, find_packages

setup(
    name="franchise_monitor",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "dash>=2.11.1",
        "dash-bootstrap-components>=1.4.1",
        "pandas>=2.0.3",
        "plotly>=5.15.0",
        "numpy>=1.24.3",
        "pyyaml>=6.0.1",
        "psutil>=5.9.5",
        "requests>=2.31.0",
        "xlsxwriter>=3.1.2",
        "aiohttp>=3.8.5",
        "python-dotenv>=1.0.0",
    ],
)