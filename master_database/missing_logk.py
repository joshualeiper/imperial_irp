import pandas as pd


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
