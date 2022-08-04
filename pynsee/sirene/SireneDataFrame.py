import pandas as pd


class SireneDataFrame(pd.DataFrame):
    """Class for handling dataframes built from INSEE SIRENE API's data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return SireneDataFrame

    from pynsee.sirene.get_location import get_location
