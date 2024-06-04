from setuptools import find_packages, setup

setup(
    name="gingr_reports",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "black",
        "certifi",
        "charset-normalizer",
        "click",
        "idna",
        "isort",
        "mypy-extensions",
        "packaging",
        "pathspec",
        "platformdirs",
        "requests",
        "setuptools",
        "urllib3",
        "wheel",
        "python-quickbooks",
        "intuit-oauth",
    ],
    entry_points={
        "console_scripts": ["run_monthly_accrual=reports.monthly_accrual_report:main"]
    },
)
