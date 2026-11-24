from setuptools import find_namespace_packages, setup

setup(
    name="cli-anything-phorme",
    version="1.0.0",
    description="The Phorme Training MCP server as a command line for people and agents (a CLI-Anything harness).",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={"cli_anything.phorme": ["skills/*.md", "README.md"]},
    install_requires=["click>=8", "prompt_toolkit>=3"],
    extras_require={"test": ["pytest>=7"]},
    python_requires=">=3.10",
    entry_points={"console_scripts": ["cli-anything-phorme=cli_anything.phorme.phorme_cli:main"]},
    license="MIT",
)
