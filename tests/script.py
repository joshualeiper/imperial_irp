import importlib.resources as pkg_resources
import master_database


def main():
    db = pkg_resources.files('master_database.databases').joinpath('llnl.dat')
    print(db)

if __name__ == '__main__':
    main()