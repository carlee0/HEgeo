import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hegeo",
    version="0.0.1",
    author="Carmen Lee",
    author_email="mailtocarmenlee@gmail.com",
    description="Geo fencing using homomorphic encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CarmenLee111/HEgeo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)