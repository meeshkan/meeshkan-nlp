import os
import sys
from shutil import rmtree

from setuptools import Command, errors, find_packages, setup

# Package meta-data.
NAME = "Mem NLP"
DESCRIPTION = "Reverse engineer services with NLP"
URL = "http://github.com/meeshkan/mem-nlp"
EMAIL = "dev@meeshkan.com"
AUTHOR = "Meeshkan Dev Team"
REQUIRES_PYTHON = ">=3.6.0"

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

REQUIRED = [
    'dataclasses;python_version<"3.7"',  # for 3.6, as it ships with 3.7
    "openapi-typed_2>=0.0.4",
    "http-types>=0.0.15,<0.1.0",
    "http-types>=0.0.15,<0.1.0",
    "jsonpath-rw>=1.4.0",
    "spacy",
    "en_core_web_lg @ https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.2.5/en_core_web_lg-2.2.5.tar.gz",
]

DEPENDENCY_LINKS = [
    "https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.2.5/en_core_web_lg-2.2.5.tar.gz"
]

BUNDLES = {}

# Requirements of all bundles
BUNDLE_REQUIREMENTS = [dep for _, bundle_dep in BUNDLES.items() for dep in bundle_dep]

DEV = BUNDLE_REQUIREMENTS + [
    "black==19.10b0",
    "flake8",
    "isort",
    "mypy",
    "pyhamcrest",
    "pylint",
    "pytest",
    "pytest-testmon",
    "pytest-watch",
    "requests-mock",
    "setuptools",
    "twine",
    "wheel",
]

VERSION = "0.0.1"


EXTRAS = dict(**BUNDLES, dev=DEV)


def run_sys_command(cmd, error_msg):
    """Run command in os.system(), raise if exit_code non-zero.

    Arguments:
        cmd {[type]} -- Command to run. For example: "pytest"
        error_msg {[type]} -- Error message to raise at failure

    Raises:
        errors.DistutilsError: Exited with non-zero exit code.
    """
    exit_code = os.system(cmd)
    if exit_code != 0:
        raise errors.DistutilsError(error_msg)


class SetupCommand(Command):
    """Base class for setup.py commands with no arguments"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def rmdir_if_exists(self, directory):
        self.status("Deleting {}".format(directory))
        rmtree(directory, ignore_errors=True)


BUILD_COMMAND = "{executable} setup.py sdist bdist_wheel --universal".format(
    executable=sys.executable
)

TYPE_CHECK_COMMAND = "pyright --lib"

TEST_COMMAND = "pytest ./tests"

LINT_COMMAND = "flake8 --exclude .git,.venv,__pycache__,build,dist"

BLACK_FORMAT_COMMAND = "black ."
ISORT_FORMAT_COMMAND = "isort -y"

BLACK_CHECK_COMMAND = "black --check ."
ISORT_CHECK_COMMAND = "pipenv run isort --check-only -v"


def build():
    run_sys_command(BUILD_COMMAND, "Build failed")


def type_check():
    run_sys_command(TYPE_CHECK_COMMAND, "Type-checking failed")


def run_tests():
    run_sys_command(TEST_COMMAND, "Tests failed")


def check_style():
    run_sys_command(LINT_COMMAND, "Checking style failed")


def enforce_formatting():
    run_sys_command(ISORT_FORMAT_COMMAND, "Formatting with isort failed")
    run_sys_command(BLACK_FORMAT_COMMAND, "Formatting with black failed")


def check_formatting():
    run_sys_command(ISORT_CHECK_COMMAND, "Checking with isort failed")
    run_sys_command(BLACK_CHECK_COMMAND, "Checking with black failed")


class BuildDistCommand(SetupCommand):
    """Support setup.py upload."""

    description = "Build the package."

    def run(self):
        self.status("Removing previous builds...")
        self.rmdir_if_exists(os.path.join(here, "dist"))
        self.status("Building Source and Wheel (universal) distribution...")
        build()


class FormatCommand(SetupCommand):
    """Enforce formatting."""

    description = "Enforce formatting."

    def run(self):
        enforce_formatting()


class TypeCheckCommand(SetupCommand):
    """Run type-checking."""

    description = "Run type-checking."

    def run(self):
        type_check()


class TestCommand(SetupCommand):
    """Support setup.py test."""

    description = "Run tests, formatting, type-checks, and linting"

    def run(self):
        self.status("Running pytest...")
        run_tests()

        self.status("Checking formatting...")
        check_formatting()

        self.status("Checking style...")
        check_style()

        self.status("Checking types...")
        type_check()


class UploadCommand(SetupCommand):
    """Support setup.py upload."""

    description = "Build and publish the package."

    def run(self):

        self.status("Removing previous builds...")
        self.rmdir_if_exists(os.path.join(here, "dist"))

        self.status("Building Source and Wheel (universal) distribution...")
        build()

        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")

        self.status("Pushing git tags...")
        os.system("git tag v{about}".format(about=VERSION))
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=REQUIRED,
    dependency_links=DEPENDENCY_LINKS,
    extras_require=EXTRAS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    cmdclass={
        "dist": BuildDistCommand,
        "format": FormatCommand,
        "upload": UploadCommand,
        "test": TestCommand,
        "typecheck": TypeCheckCommand,
    },
)
