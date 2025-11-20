"""Setup configuration for circle-draw-benchmark."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="circle-draw-benchmark",
    version="0.1.0",
    author="userhuge",
    description="Benchmark suite for evaluating LLM performance on SVG circle generation with overlap constraints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/userhuge/circle-draw-benchmark",
    py_modules=["main"],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "llm": ["litellm>=0.1.0"],
        "dev": [
            "pytest>=7.0.0",
            "coverage>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.9",
            "jupyter>=1.0.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
    ],
    entry_points={
        "console_scripts": [
            "circle-draw-benchmark=main:main",
        ],
    },
)
