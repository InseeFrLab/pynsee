
import pandas as pd

class GeoDataframe(pd.DataFrame):
    """Class for handling dataframes built from IGN's geographical data

    """    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GeoDataframe

    from pynsee.geodata.get_geom import get_geom
    from pynsee.geodata.translate_overseas import translate_overseas
