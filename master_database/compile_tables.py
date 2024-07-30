import parser_dat as parser_dat
import numpy as np
import pandas as pd
import re


class MissingSolutionSpecies:
    def __init__(self, mst: pd.DataFrame, sp: pd.DataFrame) -> None:
        self.mst = mst
        self.sp = sp
        self.mst['bool'] = self.mst['species'].apply(self.custom_apply)
        if self.mst['bool'].any():
            print('MissingSolutionSpecies: Not all species were found in the database')
            self.mst.apply(self.custom_apply1, axis=1)
            self.__init__(self.mst, self.sp)
        else:
            print('MissingSolutionSpecies: All species were found in the database')

    def custom_apply(self, x: pd.Series) -> bool:
        return self.sp[(self.sp['log_k'] == 0) & (self.sp['equation'].str.contains(x, regex=False))].empty

    def custom_apply1(self, x: pd.Series) -> None:
        if x['bool']:
            result = self.log_k(x['species'])
            self.sp = pd.concat([self.sp, result.to_frame().T], ignore_index=True)

    def log_k(self, species) -> pd.Series:
        row_data = {col: None for col in self.sp.columns}
        row_data['equation'] = f"{species} = {species}"
        row_data['log_k'] = 0.0
        row_data['source'] = 'was_missing'
        return pd.Series(row_data)


def compile_master_solution_table(list_of_databases: list, ignore=None) -> pd.DataFrame:
    result = parser_dat.MasterSolutionParser()
    for database in list_of_databases:
        result += parser_dat.MasterSolutionParser(database)
    result.data_frame = result.data_frame.dropna(axis=0, subset=['element', 'species', 'gfw_formula'])
    result.data_frame['element'] = result.data_frame['element'].apply(replace_elements)
    result.data_frame = result.data_frame.drop_duplicates(subset=['element', 'species'])
    result.data_frame['source'] = result.data_frame['source'].apply(lambda x: f'#{x}')
    return result.data_frame


def compile_solution_species_table(list_of_databases: list, ignore=None) -> pd.DataFrame:
    # init result
    result = parser_dat.SolutionParser(list_of_databases[0]).parse_file()

    # loop through all databases
    for database in list_of_databases[1:]:
        result = pd.concat([result, parser_dat.SolutionParser(database).parse_file()])

    # drop empty columns
    result = result.dropna(axis=1, how='all')

    # drop rows with missing species or element
    result = result.dropna(subset=['equation', 'log_k'])

    # drop duplicate rows
    result = result.drop_duplicates(subset=['equation'])

    # convert log_k and llnl_gamma to float
    result['log_k'] = result['log_k'].apply(lambda x: float(x[0].strip(';')) if ';' in x[0] else float(x[0]))
    if 'llnl_gamma' in result.columns:
        result['llnl_gamma'] = result['llnl_gamma'].apply(lambda x: float(x[0]) if x else None)

    # remove 1.0000 from equations
    result['equation'] = remove_ones(result['equation'])

    # Change mulitple ---- to -4, --- to -3, -- to -2
    result['equation'] = result['equation'].apply(replace_charges)

    # remove decimals from equations
    result['equation'] = strfloat_to_strint(result['equation'])

    # clean vm column
    if 'v_m' in result.columns:
        result['v_m'] = result['v_m'].apply(clean_vm)

    # clean dw column
    if 'd_w' in result.columns:
        result['d_w'] = result['d_w'].apply(clean_dw)

    # reset index and drop index column
    result = result.reset_index().drop('index', axis=1)

    return result


def compile_phase_table(list_of_databases: list, ignore=None) -> pd.DataFrame:
    # init result
    result = parser_dat.PhaseParser(list_of_databases[0]).parse_file()

    # loop through all databases
    for database in list_of_databases[1:]:
        result = pd.concat([result, parser_dat.PhaseParser(database).parse_file()])

    # drop empty rows
    result = result.dropna(axis=0, thresh=3)

    # drop duplicate rows
    result = result.drop_duplicates(subset=['phase_name', 'dissolution_reaction'])

    # convert dissolution_reaction to string
    result['dissolution_reaction'] = result['dissolution_reaction'].apply(tuple_to_string)

    # clean up vm column
    if 'v_m' in result.columns:
        result['v_m'] = result['v_m'].apply(clean_vm)

    # breakup tc column
    result = result.apply(expand_tc, axis=1)

    tupe_to_float_columns = ['t_c', 'p_c', 'omega']
    for column in tupe_to_float_columns:
        result[column] = result[column].apply(tuple_to_float)

    # remove 1.0000 from equations
    result['dissolution_reaction'] = remove_ones(result['dissolution_reaction'])

    # remove decimals from equations where possible
    result['dissolution_reaction'] = strfloat_to_strint(result['dissolution_reaction'])

    # Change ---- to -4, --- to -3, -- to -2
    result['dissolution_reaction'] = result['dissolution_reaction'].apply(replace_charges)

    # Seperate log_k and delta_h
    result[['log_k', 'delta_h']] = result.apply(expand_logk, axis=1)

    # convert log_k tuple to float
    result['log_k'] = result['log_k'].apply(tuple_to_float)

    # replace all np.nan with None
    result = result.replace({np.nan: None})

    # remove surface master species row
    try:
        surface_species_index = result[result['phase_name'] == 'SURFACE_SPECIES'].index[0]
        result = result.drop(index=surface_species_index)
    except IndexError:
        pass

    # reset index and drop index column
    result = result.reset_index().drop('index', axis=1)
    return result


def replace_charges(value):
    value = re.sub(r'----', '-4', value)
    value = re.sub(r'---', '-3', value)
    value = re.sub(r'--', '-2', value)
    return value


def replace_elements(value):
    # Find all matches of elements in the format 'Element(Number)'
    matches = re.findall(r'([A-Za-z]+)\((?!0\b)(\d+)\)', value)
    for match in matches:
        element, number = match
        # Replace the matched pattern with 'Element(+Number)'
        value = value.replace(f'{element}({number})', f'{element}(+{number})')
    return value


def tuple_to_string(tup: tuple) -> str:
    '''Converts a tuple to a string by joining all elements with a space'''
    return ' '.join(tup)


def tuple_to_float(tup: tuple) -> float:
    if tup and not isinstance(tup, float):
        try:
            return float(tup[0])
        except ValueError:
            result = tup[0].split(';')
            return float(result[0])


def remove_ones(equation: pd.Series) -> pd.Series:
    ones = re.compile(r'\b1\.0000?\b\s?')
    return equation.str.replace(ones, '', regex=True)


def strfloat_to_strint(equation: pd.Series) -> pd.Series:
    decimals = re.compile(r'\.0000?[ ]?')
    return equation.str.replace(decimals, '', regex=True)


def clean_vm(tup: tuple) -> tuple:
    result = []
    if tup:
        for t in tup:
            if 'vm' not in t.lower():
                try:
                    t = float(t)
                    result.append(t)
                except ValueError:
                    result.append(t)
        return tuple(result)


def clean_dw(tup: tuple) -> tuple:
    result = []
    if tup:
        for t in tup:
            if 'dw' not in t.lower():
                try:
                    t = float(t)
                    result.append(t)
                except ValueError:
                    result.append(t)
        return tuple(result)


def expand_tc(row):
    pc_ex = re.compile(r'\W?[Pp]_?[Cc]')
    omega_ex = re.compile(r'\s?\W?[Oo]mega')
    t_c_combined = row['t_c']
    t_c, p_c, omega = 0.0, 0.0, 0.0
    if t_c_combined and len(t_c_combined) > 1:
        for i, entry in enumerate(t_c_combined):
            if i == 0:
                t_c = float(entry.strip(';'))
            elif pc_ex.search(entry):
                p_c = float(t_c_combined[i+1].strip(';'))
            elif omega_ex.search(entry):
                omega = float(t_c_combined[i+1].strip(';'))
        row['p_c'] = p_c
        row['omega'] = omega
        row['t_c'] = t_c
    return row


def expand_logk(row):
    log_k_value = row['log_k']
    if log_k_value and len(log_k_value) > 1:
        log_k_corrected = (log_k_value[0],)
        delta_h_corrected = []
        for i, entry in enumerate(log_k_value):
            if i == 0:
                continue
            elif 'delta_h' not in entry.lower():
                delta_h_corrected.append(entry)
        delta_h_corrected = tuple(delta_h_corrected)
        # try:
        #     delta_h_corrected = (log_k_value[1], log_k_value[2], log_k_value[3])
        #     print(delta_h_corrected)
        # except IndexError:
        #     delta_h_corrected = (log_k_value[1], log_k_value[2])
        return pd.Series([log_k_corrected, delta_h_corrected])
    else:
        return pd.Series([log_k_value, row['delta_h']])
