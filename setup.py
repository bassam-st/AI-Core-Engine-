from setuptools import setup, find_packages

setup(
    name="ai-core-engine",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "gunicorn==21.2.0", 
        "requests==2.31.0",
    ],
    python_requires=">=3.7",
)
