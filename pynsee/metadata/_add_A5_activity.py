
import pandas as pd

def _get_A5_activity_label():
    
    A5 = pd.DataFrame(
        {'A5': ['AZ', 'BE', 'FZ', 'GU', 'OQ'],
        'TITLE_A5_FR': ['Agriculture, sylviculture et pêche',
        'Industrie manufacturière, industries extractives et autres',
        'Construction', 'Services principalement marchands',
        'Services principalement non marchands'],
        'TITLE_A5_EN': ['Agriculture, forestry, and fisheries',
        'Mining, quarrying and manufacturing',
        'Construction', 'Mainly market services', 'Mainly non-market services']}
    )

    return A5




