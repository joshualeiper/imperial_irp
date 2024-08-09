import compile_tables as ct
import compile_file as cf
import parser_dat as p
from named_expressions import NAMED_EXPRESSIONS


def main():
    """
    Main function for the program.
    """
    db_list = p.phreeqc_database_list('databases/test_data')
    mst = ct.compile_master_solution_table(db_list)
    sp = ct.compile_solution_species_table(db_list)
    # Fill in missing log_k = 0.0 equations
    # missing = ct.MissingSolutionSpecies(mst, sp)
    # sp = missing.sp
    phases = ct.compile_phase_table(db_list)
    with open('master_database.dat', 'w', encoding='utf-8') as f:
        f.write(NAMED_EXPRESSIONS)
        f.write("SOLUTION_MASTER_SPECIES\n#element\tmaster species\talkalinity\tgfw|formula\tgfw of element\tsource\n")
        mst.apply(lambda row: cf.write_mst(row, f), axis=1)
        f.write("\nSOLUTION_SPECIES\n")
        sp.apply(lambda row: cf.write_sp(row, f), axis=1)
        f.write("\nPHASES\n")
        phases.apply(lambda row: cf.write_phase(row, f), axis=1)

    print("File processing complete.")


if __name__ == '__main__':
    main()
