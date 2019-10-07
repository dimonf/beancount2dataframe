import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["beancount","pandas"]

setuptools.setup(
        name="beancount2dataframe",
        version="0.0.1",
        author="Dmitri Kourbatsky",
        author_email="camel109@gmail.com",
        decription="pandas driver to load and read beancount records",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/dimonf/beancount2dataframe.git",
#        packages = setuptools.find_packages(),
        packages = ['beancount2dataframe'],
        package_dir={'beancount2dataframe':'src'},
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
        install_requires=requirements,
)

