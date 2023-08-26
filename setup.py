import os
from setuptools import find_packages, setup
with open(os.path.join("README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open(os.path.join("requirements.txt"), "r", encoding="utf-8") as fh:
    requirements = fh.read()

VERSION="0.9.0"
setup(
    name = 'cfn-docgen',
    version = VERSION,
    author = 'Takehiro Horie',
    author_email = 'horie.takehiro@outlook.jp',
    license = 'MIT License',
    description = 'Document generator from cfn template files.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/horietakehiro/cfn-docgen',
    package_dir={"": "src"},
    packages = find_packages(where="src", ),
    install_requires = [requirements],
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        cfn-docgen=cfn_docgen.entrypoints.cli.main:main
    '''
)