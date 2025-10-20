from setuptools import setup, find_packages

setup(
    name="ai-core-engine",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.3",
        "gunicorn>=21.2.0",
        "requests>=2.31.0",
        "numpy>=1.24.3",
        "nltk>=3.8.1",
        "scikit-learn>=1.3.0",
        "sentence-transformers>=2.2.2",
        "torch>=2.3.0",
        "transformers>=4.30.2"
    ],
    python_requires=">=3.8",
)
