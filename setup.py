import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="terminator-layout-builder",  # Replace with your own username
    version="0.1.1",
    author="Faiz Shukri",
    author_email="faizshukri90@gmail.com",
    description="A Terminator Terminal Layout Builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/faizshukri/terminator-layout-builder",
    license="MIT",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["configobj", "pydash", "pyyaml", "expandvars"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={"console_scripts": ["tlb=builder.__main__:main"]},
)
