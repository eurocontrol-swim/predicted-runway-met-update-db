import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="predicted-runway-met-update-db",
    version="0.0.1",
    author="EUROCONTROL (SWIM)",
    author_email="alexandros.ntavelos.ext@eurocontrol.int",
    description="Accessing the met-update DB of the web app of the InnoHub Predicted Runway In-Use project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eurocontrol-swim/predicted-runway-met-update-db",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        'pymongo',
        'mongoengine'
    ],
    tests_require=[
        'pytest',
        'pytest-cov'
    ],
    platforms=['Any'],
    license='see LICENSE',
)
