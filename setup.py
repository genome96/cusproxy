from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vps-proxy-kit",
    version="1.0.0",
    author="VPS Proxy Kit Team",
    author_email="admin@example.com",
    description="Production-ready proxy server management system for Ubuntu 22.04",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vps-proxy-kit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Proxy Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.7",
        "argon2-cffi>=23.1.0",
        "sqlalchemy>=2.0.23",
        "cryptography>=41.0.7",
        "psutil>=5.9.6",
        "prometheus-client>=0.19.0",
        "pyyaml>=6.0.1",
        "watchdog>=3.0.0",
        "tabulate>=0.9.0",
        "python-dateutil>=2.8.2",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "api": [
            "fastapi>=0.108.0",
            "uvicorn>=0.25.0",
            "pydantic>=2.5.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "vpk=vpk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "vpk": ["*.yml", "*.yaml"],
    },
    zip_safe=False,
)
