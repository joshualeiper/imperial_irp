import re
import logging
import pandas as pd
import compile_tables as ct
import compile_file as cf
import parser_dat as p
from named_expressions import NAMED_EXPRESSIONS

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


def compile_and_rank_mst(db_list):
    mst = ct.compile_master_solution_table(db_list)
    mst['priority'] = mst['source'].apply(lambda x: RANK[x] if x in RANK else 5)
    return mst.sort_values(by=['priority'])


def add_hash_to_source(source):
    if source[0] == '#':
        return source
    return '#' + source


def remove_hash_from_source(source):
    if source[0] == '#':
        return source[1:]
    return source


def get_missing_species(mst, result_mst, add='#minteq.v4.dat'):
    add = add_hash_to_source(add)
    temp = mst[mst['source'] == add]
    missing = ~temp['element'].isin(result_mst['element'])
    return temp[missing]


def process_missing_species(missing_species):
    missing_species = missing_species[~missing_species['species'].isin(TO_DROP)]
    return missing_species


def find_and_collect_matches(series, entry, all_match_indexes, no_matches):
    if entry == 'Sb(OH)6-':
        logging.warning('Unexpected species Sb(OH)6- found')
    match_indexes = series[series.str.contains(entry, regex=False)].index.tolist()
    if match_indexes:
        all_match_indexes.extend(match_indexes)
    else:
        no_matches.append(entry)


def reorder_file_list(file_list, rank_dict):

    # Extract filenames from the paths
    filenames = [path.split('/')[-1] for path in file_list]

    # Separate the files based on their presence in the ranking dictionary
    ranked_files = [file for file in filenames if f'#{file}' in rank_dict]
    unranked_files = [file for file in filenames if f'#{file}' not in rank_dict]

    # Sort the ranked files according to the ranking dictionary
    ranked_files.sort(key=lambda x: rank_dict[f'#{x}'])

    # Combine the sorted ranked files with the remaining unranked files
    sorted_filenames = ranked_files + unranked_files

    # Recreate the file paths in the new order
    sorted_file_paths = [f'#{filename}' for filename in sorted_filenames]

    return sorted_file_paths


def main():
    db_list = p.phreeqc_database_list(DB_PATH)
    mst = compile_and_rank_mst(db_list)
    sp = ct.compile_solution_species_table(db_list)

    # Reorder the file list based on the ranking dictionary and change from file paths to source names
    db_list = reorder_file_list(db_list, RANK)
    result_mst = mst[mst['source'] == db_list[0]]
    result_sp = sp[sp['source'] == remove_hash_from_source(db_list[0])]

    all_match_indexes = []
    for i in range(1, len(db_list)):
        missing_species = get_missing_species(mst, result_mst, db_list[i])
        if missing_species.empty:
            logging.info("No missing species found in %s", db_list[i])
            continue

        if db_list[i] == '#minteq.v4.dat':
            missing_species = process_missing_species(missing_species)

        equations = sp[sp['source'] == remove_hash_from_source(db_list[i])]['equation']

        no_matching_equations = []
        missing_species['species'].apply(
            lambda entry: find_and_collect_matches(
                equations,
                entry,
                all_match_indexes,
                no_matching_equations
                )
            )
        result_mst = pd.concat([result_mst, missing_species], ignore_index=True)
    all_match_indexes = list(set(all_match_indexes))
    equations_add = sp.loc[all_match_indexes]

    drop_re = re.compile('Hg[(]OH[)]2|Sb[(]OH[)]6-|H4[(]SiO4[)]|H2[(]PO4[)]-')
    drop_index = equations_add[equations_add['equation'].str.contains(drop_re)].index
    equations_add = equations_add.drop(index=drop_index)

    result_sp = pd.concat([result_sp, equations_add], ignore_index=True)
    result_mst = result_mst.sort_values(by=['element'])

    with open('master_database.dat', 'w', encoding='utf-8') as f:
        f.write(NAMED_EXPRESSIONS)
        f.write("SOLUTION_MASTER_SPECIES\n#element\tmaster species\talkalinity\tgfw|formula\tgfw of element\tsource\n")
        result_mst.apply(lambda row: cf.write_mst(row, f), axis=1)
        f.write("\nSOLUTION_SPECIES\n")
        result_sp.apply(lambda row: cf.write_sp(row, f), axis=1)

    logging.info("File processing complete.")


if __name__ == "__main__":
    main()
