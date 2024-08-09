"""Compile multiple databases into a single master database."""
import re
import logging
import pandas as pd
import master_database.compile_file as cf
import master_database.compile_tables as ct
import master_database.parser_dat as p
from master_database.named_expressions import NAMED_EXPRESSIONS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants
DB_PATH = 'databases/test_data'
RANK = {
    '#llnl.dat': 1,
    '#minteq.v4.dat': 2,
    '#phreeqc.dat': 3,
    '#Tipping_Hurley.dat': 4,
}
TO_DROP = ['Hg', 'Sb(OH)6-']


def compile_and_rank_mst(db_list: str) -> pd.DataFrame:
    """
    Compile and rank the master solution table.
    Parameters
    ----------
    db_list : list
        A list of database names.
    Returns
    -------
    pandas.DataFrame
        The compiled and ranked master solution table.
    Notes
    -----
    This function compiles the master solution table using the given list of database names.
    It assigns a priority to each row in the table based on the 'source' column.
    The priority is determined by looking up the 'source' value in the RANK dictionary.
    If the 'source' value is not found in the RANK dictionary, a default priority of 5 is assigned.
    The resulting table is then sorted by the 'priority' column.
    """
    mst = ct.compile_master_solution_table(db_list)
    mst['priority'] = mst['source'].apply(lambda x: RANK[x] if x in RANK else 5)
    return mst.sort_values(by=['priority'])


def add_hash_to_source(source: str) -> str:
    """
    Add a hash symbol to the beginning of the source if it is not already present.

    Parameters:
    source (str): The source string to add a hash symbol to.

    Returns:
    str: The modified source string with a hash symbol added.

    """
    if source[0] == '#':
        return source
    return '#' + source


def remove_hash_from_source(source: str) -> str:
    """
    Remove the hash symbol from the beginning of the source string.

    Parameters:
    source (str): The source string.

    Returns:
    str: The source string without the hash symbol at the beginning.

    """
    if source[0] == '#':
        return source[1:]
    return source


def get_missing_species(mst: pd.DataFrame, result_mst: pd.DataFrame, add: str = '#minteq.v4.dat') -> pd.DataFrame:
    """
    Get the missing species from the master database.

    Parameters:
        mst (pd.DataFrame): The master database.
        result_mst (pd.DataFrame): The result master database.
        add (str, optional): The source to add. Defaults to '#minteq.v4.dat'.

    Returns:
        pd.DataFrame: The missing species from the master database.
    """
    add = add_hash_to_source(add)
    temp = mst[mst['source'] == add]
    missing = ~temp['element'].isin(result_mst['element'])
    return temp[missing]


def process_missing_species(missing_species: pd.DataFrame) -> pd.DataFrame:
    """
    Process missing species data by removing rows with species in TO_DROP.

    Parameters
    ----------
    missing_species : pandas.DataFrame
        DataFrame containing missing species data.

    Returns
    -------
    pandas.DataFrame
        DataFrame with rows removed where species is in TO_DROP.
    """
    missing_species = missing_species[~missing_species['species'].isin(TO_DROP)]
    return missing_species


def find_and_collect_matches(series: pd.Series, entry: str, all_match_indexes: list) -> None:
    """
    Find and collect matches in a series based on a given entry.

    Parameters:
    -----------
    series : pandas.Series
        The series to search for matches.
    entry : str
        The entry to search for in the series.
    all_match_indexes : list
        The list to collect all the match indexes.

    Returns:
    --------
    None

    Raises:
    -------
    None

    Notes:
    ------
    - If the entry is 'Sb(OH)6-', a warning message will be logged.
    - The function searches for matches in the series based on the entry.
    - The match indexes are collected in the all_match_indexes list.
    """
    if entry == 'Sb(OH)6-':
        logging.warning('Unexpected species Sb(OH)6- found')
    match_indexes = series[series.str.contains(entry, regex=False)].index.tolist()
    if match_indexes:
        all_match_indexes.extend(match_indexes)


def reorder_file_list(file_list: str, rank_dict: dict) -> list:
    """
    Reorders a list of file paths based on a ranking dictionary.

    Parameters:
    - file_list (list): A list of file paths.
    - rank_dict (dict): A dictionary containing the ranking information.

    Returns:
    - sorted_file_paths (list): A list of file paths sorted according to the ranking dictionary.

    Example:
    >>> file_list = ['/path/to/file1.txt', '/path/to/file2.txt', '/path/to/file3.txt']
    >>> rank_dict = {'#file1.txt': 3, '#file2.txt': 1, '#file3.txt': 2}
    >>> reorder_file_list(file_list, rank_dict)
    ['#file2.txt', '#file3.txt', '#file1.txt']
    """
    filenames = [path.split('/')[-1] for path in file_list]
    ranked_files = [file for file in filenames if f'#{file}' in rank_dict]
    unranked_files = [file for file in filenames if f'#{file}' not in rank_dict]
    ranked_files.sort(key=lambda x: rank_dict[f'#{x}'])
    sorted_filenames = ranked_files + unranked_files
    sorted_file_paths = [f'#{filename}' for filename in sorted_filenames]

    return sorted_file_paths


def main():
    """Main function to compile the master database. """
    db_list = p.phreeqc_database_list(DB_PATH)
    mst = compile_and_rank_mst(db_list)
    soln_species = ct.compile_solution_species_table(db_list)
    db_list = reorder_file_list(db_list, RANK)
    result_mst = mst[mst['source'] == db_list[0]]
    result_sp = soln_species[soln_species['source'] == remove_hash_from_source(db_list[0])]

    all_match_indexes = []
    for i in range(1, len(db_list)):
        missing_species = get_missing_species(mst, result_mst, db_list[i])
        if missing_species.empty:
            logging.info("No missing species found in %s", db_list[i])
            continue

        if db_list[i] == '#minteq.v4.dat':
            missing_species = process_missing_species(missing_species)

        equations = soln_species[soln_species['source'] == remove_hash_from_source(db_list[i])]['equation']
        missing_species['species'].apply(
            lambda entry: find_and_collect_matches(
                equations,
                entry,
                all_match_indexes,
                )
            )
        result_mst = pd.concat([result_mst, missing_species], ignore_index=True)

    all_match_indexes = list(set(all_match_indexes))
    equations_add = soln_species.loc[all_match_indexes]
    drop_re = re.compile('Hg[(]OH[)]2|Sb[(]OH[)]6-|H4[(]SiO4[)]|H2[(]PO4[)]-')
    drop_index = equations_add[equations_add['equation'].str.contains(drop_re)].index
    equations_add = equations_add.drop(index=drop_index)
    result_sp = pd.concat([result_sp, equations_add], ignore_index=True)
    result_mst = result_mst.sort_values(by=['element'])

    with open('master_database.dat', 'w', encoding='utf-8') as file:
        file.write(NAMED_EXPRESSIONS)
        file.write("SOLUTION_MASTER_SPECIES\n#element\tmaster species\talkalinity\tgfw|formula\tgfw of element\tsource\n")
        result_mst.apply(lambda row: cf.write_mst(row, file), axis=1)
        file.write("\nSOLUTION_SPECIES\n")
        result_sp.apply(lambda row: cf.write_sp(row, file), axis=1)

    logging.info("File processing complete.")


if __name__ == "__main__":
    main()
