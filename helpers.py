import pandas as pd
import json

def print_dict_subset(d, n=3):
    """
    Print primele n elemente dintr-un dictionar.
    
    Parametri:
    - d: dictionar
    - n: numar de elemente de printat (default 3)
    """
    subset = dict(list(d.items())[:n])
    print(json.dumps(subset, indent=2, ensure_ascii=False))


def read_culturi_values(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    row = df.iloc[0]  # first (and only) row
    culturi = row.iloc[:].astype(str).tolist()
    culturi = [s[:2] for s in culturi]
    return culturi

def read_temp_tabl(file_path, sheet_name, skip_rows, use_cols, nr_rows):
    """
    Citeste tabelul de temperaturi.
    Returneaza Dictionarul pe baza culturii, DataFrame-ul curat si headerul cu cele 12 valori ale temperaturii.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=skip_rows, usecols=use_cols, nrows=1)

    row = df.iloc[0]  # first (and only) row
    temperature_values = row.iloc[2:].astype(float).tolist()

    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=skip_rows+1, usecols=use_cols, nrows=nr_rows-1)
    df = df.reset_index(drop=True)

    numeric_cols = df.select_dtypes(include='number').columns
    df[numeric_cols] = df[numeric_cols].astype(float)

    first_col = df.columns[0]
    df[first_col] = df[first_col].ffill()

    second_col = df.columns[1]

    result_dict = {}
    for _, row in df.iterrows():
        key1 = row[first_col]
        key2 = row[second_col]
        values = row.drop([first_col, second_col]).to_dict()
        
        values = {str(i): v for i, (_, v) in enumerate(values.items())}

        if key1 not in result_dict:
            result_dict[key1] = {}
        result_dict[key1][key2] = values
    
    return result_dict, df, temperature_values

def read_excel_one_lvl(file_path, sheet_name, max_cols=None):
    """
    Citeste un sheet Excel care are merge cells pe header si coloana cultura.
    Returneaza Dictionarul pe baza culturii si DataFrame-ul curat .
    """
    # Citim sheet-ul fara header
    if(max_cols):
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, usecols=range(max_cols))
    else:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Preluam primele 2 randuri ca header si completam valorile goale
    header = df.iloc[0:2].ffill()

    # Setam header-ul final (randul 2 dupa forward fill)
    df.columns = header.iloc[1]

    # Scoatem primele 2 randuri folosite pentru header
    df = df.iloc[2:].reset_index(drop=True)

    # Optional: pastram doar codul culturii (primele 2 caractere)
    df['Cultura'] = df['Cultura'].str[:2]

    # Transformam in dictionar {cultura: {caracter: valoare, ...}, ...}
    result_dict = {
        row['Cultura']: row.drop('Cultura').to_dict() 
        for _, row in df.iterrows()
    }

    return result_dict, df


def read_excel_double_lvl(file_path, sheet_name, drop_empty_columns=False, skip_rows=0):
    """
    Citeste un sheet Excel cu 2 nivele de categorii pe coloane si coloana 'Cultura'.
    Returneaza Dictionar pe baza culturii si DataFrame-ul curat.
    """
    # Citim Excel fara header
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Preluam primele 2 randuri ca header si completam valorile goale
    if skip_rows > 0:
        header = df.iloc[0:2+skip_rows].ffill()
        header = header[-2:]
    else:
        header = df.iloc[0:2].ffill()

    if skip_rows > 0:
        df = df.iloc[skip_rows:].reset_index(drop=True)

    header = header.ffill(axis=1)

    # Combinam header-urile intr-un tuple (Categoria mare, Subcategoria)
    df.columns = pd.MultiIndex.from_tuples(list(zip(header.iloc[0], header.iloc[1])))

    # Scoatem randurile folosite pentru header
    df = df.iloc[2:].reset_index(drop=True)

    if drop_empty_columns:
         # 1. pastram doar coloanele care au valori reale
        non_empty_cols = [col for col in df.columns if df[col].notna().any()]
        df = df.loc[:, non_empty_cols]
    
        # RESETAM LEVEL-URILE MULTIINDEX
        df.columns = pd.MultiIndex.from_tuples(list(df.columns))

    # Optional: pastram doar codul culturii (primele 2 caractere)
    df['Cultura'] = df['Cultura'].iloc[:,0].str[:2]

    # Construim dictionarul
    result_dict = {}
    for _, row in df.iterrows():
        cultura = row[('Cultura','Cultura')]
        result_dict[cultura] = {}

        major_categories = sorted(set(col[0] for col in df.columns))

        for major_cat in major_categories:
            if major_cat == 'Cultura':
                continue
            result_dict[cultura][major_cat] = {}
            sub_cols = [col for col in df.columns if col[0]==major_cat]
            for col in sub_cols:
                result_dict[cultura][major_cat][col[1]] = row[col]
    
    return result_dict, df