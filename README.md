ScopeFoundry 2 Basic Tutorial
==================================

Roughly the content of the ScopeFoundry basic and data_browser tutorial.

<http://www.scopefoundry.org>

ScopeFoundry is a Python platform for controlling custom laboratory experiments and visualizing scientific data.


Author
----------

Benedikt Ursprung

## Credits

- Parts taken from E. Barnards [HW_virtual_function_gen](https://github.com/ScopeFoundry/HW_virtual_function_gen) and prev. tutorials.

Requirements
------------

	* ScopeFoundry

Installation
------------
Download and install the Miniconda Python distribution.

Create an environment with the required dependencies. Anaconda provides a way to make a clean set of packages in an environment. To create an environment called `scopefoundry`, use the `Anaconda(3)` Prompt to run:

	conda create -n scopefoundry python=3.13

To include ScopeFoundry and all of the packages it needs to run, activate the environment:

	conda activate scopefoundry

Download and install ScopeFoundry and its dependencies:

	pip install pyqt6 qtconsole matplotlib scopefoundry
​
## Using Miniconda
With that in mind, if you want the other user to have no knowledge of your default install path, you can remove the prefix line with grep before writing to environment.yml.

	conda env export | grep -v "^prefix: " > environment.yml

Either way, the other user then runs:

	conda env create -f environment.yml

and the environment will get installed in their default conda environment path.

If you want to specify a different install path than the default for your system (not related to 'prefix' in the environment.yml), just use the -p flag followed by the required path.

	conda env create -f environment.yml -p /home/user/anaconda3/envs/env_name


History
--------

### 0.1.0	2025-01-12	Initial public release.

All components tested


### 0.1.1	2025-01-12	Adapted for ScopeFoundry 2.1 release.

All components tested
