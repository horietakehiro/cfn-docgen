import os
from setuptools import find_packages, setup
from cfn_docgen import __version__
with open(os.path.join(
    os.path.dirname(__file__), "README.md"), "r", encoding="utf-8",
) as fp:
    long_description = fp.read()
with open(os.path.join(
    os.path.dirname(__file__), "requirements.txt"), "r", encoding="utf-8"
) as fp:
    requirements = fp.read()

setup(
    name = 'cfn-docgen',
    version = __version__,
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
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        cfn-docgen=cfn_docgen.entrypoints.cli.main:main
    '''
)