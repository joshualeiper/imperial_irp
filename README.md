
# Joshua Leiper's IRP

![Code Coverage](https://img.shields.io/badge/Coverage-93%25-brightgreen) ![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)

For further details on tests, see [tests](tests/). Details of testing coverage are found in [coverage](tests/coverage.xml)

# Table of Contents
- [Description](#description)
- [Requirements](#installation-requirements)
- [Installation Guide](#installation-instructions)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Documentation](#docs)
- [Documentation](#docs)

# Description
This project provides tools for the comparative analysis and optimization of PHREEQC databases for geochemical speciation calculations. It includes scripts for database conversion, conflict resolution, and creating a unified database that combines multiple PHREEQC-provided databases.

### Features
- **PHREEQC Database Converter**: A tool that can transform PHREEQC `.dat` files into CSV or JSON for easier comparison.
- **Comparative Analysis of PHREEQC Databases**: To assist with database selection, a comparative analysis is provided.
- **Master Database**: A unified database optimized for speciation calculations in PHREEQC. Maximum possible elements in the Solution Master Species block and equations in the Solution Species block are provided in the `master_database.dat` file.

## Installation Requirements
To use this Python package, it is **strongly** recommended to use a Conda environment. This ensures dependencies are handled by the `.yml` file provided in this repository. If you *must*, you can install via `pip install .`, but this method is not suggested.

#### Requirements
- Python == 3.1X: Some version of Python 3.1X must be used for compatibility with PHREEQCPython.
- click >= 8.0.3
- numpy >= 2.1.0
- pandas >= 2.2.2
- phreeqpython >= 1.5.2
- pytest >= 8.3.2
- seaborn >= 0.13.0

All requirements are updated in the `requirements.txt` file in this library to ensure a smooth `pip install .` style installation.

## Installation Instructions
[Install with Conda (recommended)](#create-conda-environment)

[Install with PIP](#pip-install)

To clone this repository, navigate to the folder where you want the project to live:

```bash
cd to/desired/folder
```

Now, clone the repo into the folder:

```bash
git clone https://github.com/ese-msc-2023/irp-jjl122
```

Move the terminal into the project repository folder:

```bash
cd irp-jjl122
```

### Create Conda Environment

Run the following code in the terminal to create and activate the new Conda environment:

```bash
conda deactivate
conda env create -f environment.yml
conda activate josh_2024
```

### Pip Install

Ensure you are in the directory planned for the project and run:

```bash
pip install .
```

Using this method may result in conflicts between numpy, pandas, and matplotlib versions, throwing a ton of warnings upon database generation.

## Usage
[Raw Parsing Tool](#parser)

[Generate Master Database](#database-generation)

There are two main user-facing tools in the repo: a parsing tool for converting PHREEQC `.dat` files into CSV and JSON formats, and a tool to generate a new Master database.

#### Parser
To use the parser:

1. Navigate into the `build_database` folder:

    ```bash
    cd build_database
    ```

**Viewing Help Messages**  
To see all options for the `parser_dat.py` file, run:

```bash
python parser_dat.py --help 
```

Usage: 
```bash
parser_dat.py [OPTIONS] DATABASE_FILE

  Parses a PHREEQC database file and outputs data as CSVs.

  DATABASE_FILE: Path to the PHREEQC database file.

Options:
  --solution_csv TEXT         Filename for solution data CSV
  --master_solution_csv TEXT  Filename for master solution data CSV
  --save_solution             Save solution data CSV
  --save_master_solution      Save master solution data CSV
  --help                      Show this message and exit.
```

2. **Basic Parsing and Saving Solution Data to CSV**

To parse a PHREEQC database file and save the solution species data to a CSV file, use the following command:

```bash
python parse_phreeqc.py path/to/phreeqc_database.dat --save_solution
```

This command will parse the specified PHREEQC database file and save the solution species data to `solution_data.csv` by default.

3. **Parsing and Saving Master Solution Data to a Specific CSV File**

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
python __main__.py --help
```

Usage:
```bash
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

For examples of internal functions and tools, please see the results [README](results/README.md).

## Project Structure
A file tree of the project is:

```
IRP-JJL122/
├── build_database/
│   ├── databases/
│   │   └── ...
│   ├── __main__.py
│   ├── clean_tables.py
│   ├── named_expressions.py
│   ├── parser_dat.py
│   ├── utils.py
│   ├── write_dataframes.py
│   └── README.md
├── results/
│   ├── compare_database.ipynb
│   ├── master_dat_performance.ipynb
│   ├── utils.py
│   └── README.md
└── tests/
    └── ...
environment.yml
README.md
references.md
requirements.txt
setup.py
```

### Testing
To run the testing framework, simply use the pytest command in the terminal:

```bash
pytest tests/
```

### Documentation
For details on documentation, please refer to the Sphinx autodocs in the [docs](./docs/_build/html) folder. You can view this documentation if you have cloned the repo locally by launching the [index](./docs/_build/html/index.html) file in your favorite browser.
