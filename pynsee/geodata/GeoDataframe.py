

class GeoDataframe(pd.DataFrame):
    """Class for handling dataframes built from IGN's geographical data

    """    

    @property
    def _constructor(self):
        return GeoDataframe
    
    from pynsee.geodata.get_geom import get_geom
    from pynsee.geodata.translate_overseas import translate_overseas
    from pynsee.geodata.zoom_paris import zoom_paris

    
