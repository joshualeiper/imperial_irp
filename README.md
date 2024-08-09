# Joshua Leiper's IRP

## Installing requirements

### Cloning the repo

In order to clone this repository, navigate to the file where you want the project to live
```bash
cd to/desired/folder
```
Now clone the repo into the folder

```bash
git clone https://github.com/ese-msc-2023/irp-jjl122
```
### Create Conda environment

move the terminal into the project repository folder

```bash
cd irp-jjl122
```

Run the following code in the terminal to create and activate the new environment

```bash
conda deactivate
conda env create -f environment.yml
conda activate josh_2024
```

Create a combined llnl + minteq database
```bash
python master_database/
```
The terminal should print a logging message that says "File processing complete". If this check to see if a file names master_database.dat has been created. This new file can be used as a database file in PHREEQC for speciation calculations.
