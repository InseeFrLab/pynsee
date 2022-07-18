import pandas as pd


class GeoFrDataFrame(pd.DataFrame):
    """Class for handling dataframes built from IGN's geographical data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GeoFrDataFrame

    from pynsee.geodata.get_geom import get_geom
    from pynsee.geodata.translate import translate
    from pynsee.geodata.zoom import zoom
