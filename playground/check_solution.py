# FROM REF 1
import pandas as pd
import matplotlib.pyplot as plt


# Load the data from the text file
file_path = "playground/data/out.txt"
data = pd.read_csv(file_path, sep='\s+')

# Display the first few rows of the dataframe
print(data.head())

# Plot the data
plt.figure(figsize=(12, 8))
for column in data.columns:
    plt.plot(data[column], label=column)

plt.xlabel("Index")
plt.ylabel("Concentration")
plt.title("Elemental Concentrations Over Time")
plt.legend()
plt.grid(True)
plt.show()
