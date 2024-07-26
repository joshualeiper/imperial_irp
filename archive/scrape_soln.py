from sqlalchemy import create_engine
from master_database.parser_dat import CompoundFileParser

# Parse the file
parser = CompoundFileParser('trash_1.txt')
df = parser.parse_file()

# Convert lists to strings in the DataFrame
for col in df.columns:
    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)

# Database credentials
username = 'jjl122'
password = 'S'
host = 'localhost'
database = 'giraffe'

# Create an engine instance
engine = create_engine(
    f'mysql+pymysql://{username}:{password}@{host}/{database}'
    )

# Convert DataFrame to SQL
table_name = 'ChemicalEquations'
df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

print("DataFrame has been written to the MySQL database.")
