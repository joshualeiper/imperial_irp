import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings


def plot_conflicts(df: pd.DataFrame, title, rotation: int = 45) -> None:
    """
    Plot the distribution of conflicting attributes in a DataFrame.
    """
    sns.histplot(data=df, x='source')
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.title(title)
    plt.xticks(rotation=rotation)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        plt.gca().set_xticklabels(
            [label.get_text().replace('#', '').replace('.dat', '') for label in plt.gca().get_xticklabels()]
            )
    plt.show()


def alk_gfw_duplicates(df: pd.DataFrame, target_column: str) -> tuple[int, pd.DataFrame]:
    """
    Find duplicate rows in a DataFrame based on the target column.
    """
    if target_column not in df.columns:
        raise ValueError(f"{target_column} not in DataFrame columns")
    dups = df[['element', 'species', target_column, 'source']]
    dups = dups.drop_duplicates(subset=['element', 'species', target_column])
    dups = dups[dups.duplicated(subset=['element', 'species'], keep=False)].sort_values(by=['element'])
    dif = dups.groupby(['element', 'species']).nunique()
    unique_count = dif.shape[0]
    return unique_count, dups
