import pathlib
from setuptools import setup, find_packages


def setup_package():
    package_name = "pathy"
    root = pathlib.Path(__file__).parent.resolve()

    about_path = root / package_name / "about.py"
    with about_path.open("r", encoding="utf8") as f:
        about = {}
        exec(f.read(), about)

    requirements_path = root / "requirements.txt"
    with requirements_path.open("r", encoding="utf8") as f:
        requirements = [line.strip() for line in f]

    readme_path = root / "README.md"
    with readme_path.open("r", encoding="utf8") as f:
        long_description = f.read()
    extras = {
        "gcs": ["google-cloud-storage>=1.26.0,<2.0.0"],
        "test": ["pytest", "pytest-coverage", "mock", "typer-cli"],
    }
    extras["all"] = [item for group in extras.values() for item in group]
    setup(
        name=about["__title__"],
        description=about["__summary__"],
        author=about["__author__"],
        author_email=about["__email__"],
        url=about["__uri__"],
        version=about["__version__"],
        license=about["__license__"],
        long_description=long_description,
        long_description_content_type="text/markdown",
        include_package_data=True,
        packages=find_packages(),
        python_requires=">= 3.6",
        install_requires=requirements,
        extras_require=extras,
        entry_points="""
            [console_scripts]
            pathy=pathy.cli:app
        """,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
        ],
    )


if __name__ == "__main__":
    setup_package()
