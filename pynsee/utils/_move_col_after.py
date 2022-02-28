
def _move_col_after(df, col, col_ref):
    if col in df.columns:
        if col_ref in df.columns:
            loc_var = df.columns.get_loc(col_ref)
            col2insert = df[col]
            df = df.drop([col], axis=1)
            df.insert(loc_var + 1, col, col2insert)
    return(df)

def _move_col_before(df, col, col_ref):
    if col in df.columns:
        if col_ref in df.columns:
            loc_var = df.columns.get_loc(col_ref)
            col2insert = df[col]
            df = df.drop([col], axis=1)
            if loc_var!= 0:
                df.insert(loc_var -1, col, col2insert)
            else:
                df.insert(0, col, col2insert)            
    return(df)