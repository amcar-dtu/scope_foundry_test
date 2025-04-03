from setuptools import setup

setup(
    name="scope_foundry_2_basic_tutorial",
    version="0.0.1",
    description="Roughly the content of the ScopeFoundry basic tutorial.",
    # Author details
    author="Benedikt Ursprung",
    # Choose your license
    license="BSD",
    # package_dir={'ScopeFoundryHW.virtual_function_gen': '.'},
    # packages=['ScopeFoundryHW.virtual_function_gen',],
    package_data={
        "": [
            "README*",
            "LICENSE",  # include License and readme
            "*.ui",  # include QT ui files
        ],
    },
)
