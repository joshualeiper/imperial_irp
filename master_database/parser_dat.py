import re
import os
from dataclasses import dataclass, asdict
from typing import List
import pandas as pd


@dataclass
class SolutionData:
    equation: str = None
    log_k: float = None
    delta_h: List[float] = None
    gamma: List[float] = None
    d_w: List[float] = None
    v_m: List[float] = None
    millero: List[float] = None
    activity_water: List[float] = None
    add_logk: List[float] = None
    llnl_gamma: List[float] = None
    co2_llnl_gamma: List[float] = None
    erm_ddl: List[float] = None
    no_check: List[float] = None
    mole_balance: List[float] = None


@dataclass
class PhaseData:
    phase_name: str = None
    dissolution_reaction: str = None
    log_k: List = None
    delta_h: List = None
    analytic: List = None
    v_m: List = None
    t_c: List = None
    p_c: List = None
    omega: List = None


class BaseParser:
    def __init__(self, database_file_path, section_start, section_end) -> None:
        self.block_start = None
        self.source = file_name(database_file_path)
        self.line_list = text_selection(database_file_path, section_start, section_end)

    def parse_file(self) -> pd.DataFrame:
        block = []
        parsed_data_list = []
        for line in self.line_list:
            if '#' in line:
                continue
            if self.block_start.match(line):
                if block:
                    parsed_data = self.parse_block(block)
                    parsed_data_list.append(parsed_data)
                    block = []
            block.append(line.strip())
        if block:
            parsed_data = self.parse_block(block)
            parsed_data_list.append(parsed_data)

        data_dicts = [asdict(data) for data in parsed_data_list]
        result = pd.DataFrame(data_dicts)
        result['source'] = self.source
        return result

    def parse_block(self, block: List[str]):
        raise NotImplementedError

    def match_patterns(self, line, data_instance) -> None:
        for key, pattern in self.patterns.items():
            if pattern.match(line):
                line = line.split('#')[0]
                if key in line.split()[0].lower():
                    setattr(data_instance, key, tuple(line.split()[1:]))
                else:
                    setattr(data_instance, key, tuple(line.split()[0:]))
                break


class SolutionParser(BaseParser):
    def __init__(self, database_file_path) -> None:
        super().__init__(database_file_path, 'SOLUTION_SPECIES', 'PHASES')
        self.block_start = re.compile(r"^.*\s=\s.*")
        self.patterns = {
            "log_k": re.compile(r"^\s*[-]*log[ _]*k"),
            "delta_h": re.compile(r"\s*[-]*delta.*"),
            "analytic": re.compile(r"^\s*[-]*analytic"),
            "gamma": re.compile(r"^\s*[-]*gamma"),
            "d_w": re.compile(r"^\s*[-]*dw"),
            "v_m": re.compile(r"^\s*[-]*Vm"),
            "millero": re.compile(r"^\s*[-]*Millero"),
            "activity_water": re.compile(r"^\s*[-]*activity[ _]*water"),
            "add_logk": re.compile(r"^\s*[-]*add[ _]*logk"),
            #"llnl_gamma": re.compile(r"^\s*[-]*llnl[ _]*gamma"),
            "co2_llnl_gamma": re.compile(r"^\s*[-]*co2[ _]*llnl[ _]*gamma"),
            "erm_ddl": re.compile(r"^\s*[-]*erm[ _]*ddl"),
            "no_check": re.compile(r"^\s*[-]*no[ _]*check"),
            "mole_balance": re.compile(r"^\s*[-]*mole[ _]*balance")
        }

    def parse_block(self, block: List[str]) -> SolutionData:
        data_instance = SolutionData()
        for line in block:
            if self.block_start.match(line):
                data_instance.equation = line.strip()
            else:
                self.match_patterns(line, data_instance)
        return data_instance


class PhaseParser(BaseParser):
    def __init__(self, database_file_path) -> None:
        super().__init__(database_file_path, 'PHASES', 'EXCHANGE')
        self.block_start = re.compile(r"^(?!\s)\S+$")
        self.patterns = {
            "dissolution_reaction": re.compile(r"^.*\s=\s.*"),
            "log_k": re.compile(r"^\s*[-]*log[ _]*k"),
            "delta_h": re.compile(r"\s*[-]*delta.*"),
            "analytic": re.compile(r"^\s*[-]*analytic"),
            "v_m": re.compile(r"^\s*[-]*Vm"),
            "t_c": re.compile(r"^\s*[-]*T_c"),
            "p_c": re.compile(r"^\s*[-]*P_c"),
            "omega": re.compile(r"^\s*[-]*Omega")
        }

    def parse_block(self, block: List[str]) -> PhaseData:
        data_instance = PhaseData()
        for line in block:
            if self.block_start.match(line):
                data_instance.phase_name = line.strip()
            else:
                self.match_patterns(line, data_instance)
        return data_instance


class MasterSolutionParser:

    def __init__(self, database_file_path=None) -> None:
        self.composed_sources = []
        self.data_frame = None
        if database_file_path:
            self.source = file_name(database_file_path)
            self.composed_sources.append(self.source)
            self.species_list = text_selection(database_file_path, 'SOLUTION_MASTER_SPECIES', 'SOLUTION_SPECIES')
            self.species_list = [line.split() for line in self.species_list]
            self.make_dataframe

    @property
    def make_dataframe(self) -> None:
        data_frame = pd.DataFrame(
            self.species_list,
            columns=['element', 'species', 'alk', 'gfw_formula', 'element_gfw']
            )
        data_frame['source'] = self.source
        self.data_frame = data_frame

    def __add__(self, other: pd.DataFrame) -> pd.DataFrame:
        result = MasterSolutionParser()
        result.composed_sources = self.composed_sources + other.composed_sources
        result.data_frame = pd.concat([self.data_frame, other.data_frame])
        return result


# Utility functions
def text_selection(text_file, start_block, end_block) -> list:
    equations = []
    with open(text_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        read = False
        for line in lines:
            if line.strip() == start_block:
                read = True
                continue
            if end_block in line.strip() and read:
                read = False
                break
            if read:
                # remove comments
                if '#' in line:
                    line = line.split('#')[0]
                equations.append(line)
    return equations


def file_name(file_path: str) -> str:
    return os.path.basename(file_path)


def phreeqc_database_list(database_directory: str, ignore=None) -> list:
    database_file_paths = []
    for file in os.listdir(database_directory):
        if file.endswith(".dat") and not ignore:
            database_file_paths.append(os.path.join(database_directory, file))

    return database_file_paths
