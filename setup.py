from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="terms_of_interest",
    version="0.0.1",
    author="Joe Black",
    author_email="me@joeblack.nyc",
    description="Simple Twitter data processing pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["pydantic", "ujson", "glide==0.2.29", "nltk", "click", "pytest"],
    extras_require={"all": ["graphviz", "Columnar", "Pympler"]},
    entry_points={"console_scripts": ["toi=terms_of_interest.cli:cli"]},
)
