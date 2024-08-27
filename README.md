# Joshua Leiper's IRP

![Code Coverage](https://img.shields.io/badge/Coverage-93%25-brightgreen) ![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)

  

For further details on tests, see [tests](tests/). Details of testing coverage are found in [coverage](tests/coverage.xml)
# Table of Contents
- [Description](#descriptionn)
- [Requirements](#Installing-requirements)
- [Installation Guide](#Installation-Instructions)
- [Usage](#Usage)
- [Project Structure](#Project-Structure)
- [Testing](#Testing)

# Description
This project provides tools for the comparative analysis and optimization of PHREEQC databases for geochemical speciation calculations. It includes scripts for database conversion, conflict resolution, and creating a unified database that combines multiple PHREEQC-provided databases.
### Features
- PHREEQC database converter
Converter tool that can transform PHREEQC.dat files into csv or JSON for easier comparison
- Comparative analysis of PHREEQC databases
To assist with database selection, a comparative analysis is provided to assist with database selection
- Master Database
A unifed database is created optimized for speciation calculations in PHREEQC. Maximum possible elements in the Solution Master Species block and equations in the Solution Species block are provided in the master_database.dat file
  

## Installation requirements
In order to use this Python Package, it is **strongly** recommended you use a conda environment. This ensures dependancies are handled by the .yml file provided in this repository. If you *must*, you can install via `pip install .`  but this method is not suggested.
#### Requirements
- Python == 3.1X
Some verion of Python 3.1X must be used for compatability with PHREEQCPython
- click>=8.0.3
- numpy>=2.1.0
- pandas>=2.2.2
- phreeqpython>=1.5.2
- pytest>=8.3.2
- seaborn >= 0.13.0

All requirements are updated in the requirements.txt file in this library and ensure a smooth `pip install .` style install.
  
## Installation Instructions
[Install with Conda (recommended)](#create-conda-environment)
[Install with PIP](#pip-install)

In order to clone this repository, navigate to the folder where you want the project to live

```bash
cd  to/desired/folder
```

Now clone the repo into the folder
```bash
git  clone  https://github.com/ese-msc-2023/irp-jjl122
```
move the terminal into the project repository folder
```bash
cd  irp-jjl122
```
### Create Conda environment

Run the following code in the terminal to create and activate the new conda environment:
```bash
conda  deactivate
conda  env  create  -f  environment.yml
conda  activate  josh_2024
```
### Pip install
ensure you are in the directory planned for the projec and run:
```pip install .```
Using the method may result in conflicts between numpy, pandas, and matplotlib version, throwing a ton of warnings upon database gerneration.
## Usage
[Raw parsing tool](#parser)
[Generate Master Database](database-generation)

There are two main user-facing tools in the repo, a parsing tool for converting PHREEQC '.dat' files into csv and JSON formats, and a tool to generate a new Master database.
#### Parser
To use the parser:
1. Navigatge into the build_database folder
```bash
cd build_database
```
**Viewing Help Messages**
To see all options for the  `parser_dat.py` file run:
```bash
>>>python parser_dat.py  --help 
Usage: parser_dat.py [OPTIONS] DATABASE_FILE

  Parses a PHREEQC database file and outputs data as CSVs.

  DATABASE_FILE: Path to the PHREEQC database file.

Options:
  --solution_csv TEXT         Filename for solution data CSV
  --master_solution_csv TEXT  Filename for master solution data CSV
  --save_solution             Save solution data CSV
  --save_master_solution      Save master solution data CSV
  --help                      Show this message and exit.
```
2. Basic Parsing and Saving Solution Data to CSV

To parse a PHREEQC database file and save the solution species data to a CSV file, use the following command:

```bash
python parse_phreeqc.py path/to/phreeqc_database.dat --save_solution
```

This command will parse the specified PHREEQC database file and save the solution species data to `solution_data.csv` by default.

3. Parsing and Saving Master Solution Data to a Specific CSV File

You can specify a custom output file for the master solution data using the `--master_solution_csv` option:

```bash
python parse_phreeqc.py path/to/phreeqc_database.dat --save_master_solution --master_solution_csv custom_master_solution.csv
```
This command parses the PHREEQC database file and saves the master solution data to `custom_master_solution.csv`.
#### Database Generation
##### Viewing Help Messages

To see all available options and their descriptions for the `__main__.py` script, you can run the script with the `--help` flag in the terminal. This will provide detailed information on how to use the script and its various options.

Example Command:
```bash
>>>python __main__.py --help
usage: __main__.py [-h] [--output OUTPUT]

Compile multiple databases into a single master database.

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file path
```
To compile the master database and save it to the default output file (`master_database.dat`), simply run:
```bash
python __main__.py
```
This command compiles multiple databases into a single master database and saves it as `master_database.dat` in the current directory.


If you want to specify a custom output file for the compiled master database, use the `--output` or `-o` option:
```bash
python __main__.py --output custom_output.dat
```
OR
```bash
python __main__.py -o custom_output.dat
```
This command compiles the databases and saves the output to `custom_output.dat`.
