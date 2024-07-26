import compile_tables as ct
import compile_file as cf
import parser_dat as p

NAMED_EXPRESSIONS = """
NAMED_EXPRESSIONS
#
# formation of O2 from H2O
# 2H2O =  O2 + 4H+ + 4e-
#
    Log_K_O2
        log_k      -85.9951
        -delta_H	559.543	kJ/mol	# Calculated enthalpy of reaction	O2
#	Enthalpy of formation:	-2.9 kcal/mol
            -analytic   38.0229    7.99407E-03   -2.7655e+004  -1.4506e+001  199838.45
#	Range:  0-300

"""


def main():
    """
    Main function for the program.
    """

    db_list = p.phreeqc_database_list('databases/test_data')
    mst = ct.compile_master_solution_table(db_list)
    sp = ct.compile_solution_species_table(db_list)
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
