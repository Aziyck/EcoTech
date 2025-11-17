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
    culturi_filtered = [s[:2] for s in culturi]
    return culturi_filtered, culturi

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

def return_note_de_bonitare_dict(
        file_path="data.xlsx", 
        alunecari = "Absente",
        panta = "10%<P≤15%",
        salin_alcalin = "Slab salinizat/alcalizat",
        gleizare = "Submers",
        pseudogleizare = "Nepseudogleizat",
        adancirea_apelor_freatice = "Mijlocie",
        textura = "Lutoasă (≥55% 0,01mm+)",
        porozitatea = "P≥85%",
        ph = "pH≤3,5",
        carb = "CaCO3≤4",
        rezerva_de_humus = "160≤H<200",
        drenaj_desecare = "Nu",
        adancimea_sat = "Soluri cu grad de saturație în primii 20 de cm sau în Ap>55%"):
    """
    Returneaza dictionarul cu nota de bonitare calculata in cultura -> general
    si restul coeficientilor care au intervenit in calulul acestora
    """

    culturi, culturi_full = read_culturi_values(file_path, "Sheet1")
    
    # ------------------
    alunecari_dict, _ = read_excel_one_lvl(file_path, "Alunecări")
    # print_dict_subset(alunecari_dict)
    # print(alunecari_dict['PS']['Semistabilizate'])

    # # ------------------
    panta_dict, _ = read_excel_one_lvl(file_path, "Panta")
    # print_dict_subset(panta_dict)

    # # ------------------
    # temp_med_an_dict, _ = read_excel_one_lvl(file_path, "Temperatura medie anuală", max_cols=14)
    # print_dict_subset(temp_med_an_dict)

    # temp_dict, _, temp_arr = read_temp_tabl(file_path, "Temperatura medie anuală", skip_rows=17, use_cols='P:AC', nr_rows=13)
    # print_dict_subset(temp_dict)
    # print(temp_arr)

    # # ------------------
    # precip_dict, _ = read_excel_double_lvl(file_path, "Precipitații")
    # print_dict_subset(precip_dict)

    # # ------------------
    salin_and_alc_dict, _ = read_excel_one_lvl(file_path, "Salinizarea&Alcalizarea")
    # print_dict_subset(salin_and_alc_dict)

    # # ------------------
    gleuiz_dict, _ = read_excel_double_lvl(file_path, "Gleizarea")
    # print_dict_subset(gleuiz_dict)

    # # ------------------
    pseudogleiz_dict, _ = read_excel_one_lvl(file_path, "Pseudogleizare")
    # print_dict_subset(pseudogleiz_dict)

    # # ------------------
    adanc_ap_freat_dict, _ = read_excel_double_lvl(file_path, "Adâncimea apelor freatice", drop_empty_columns=True)
    # print_dict_subset(adanc_ap_freat_dict)

    # # ------------------
    textur_dict, _ = read_excel_double_lvl(file_path, "Textura",skip_rows=1)
    # print_dict_subset(textur_dict)

    # # ------------------
    # vol_edafil_util_dict, _ = read_excel_double_lvl(file_path, "Volumul edafic util",skip_rows=1)
    # print_dict_subset(vol_edafil_util_dict)

    # # ------------------
    porozitatea_dict, _ = read_excel_double_lvl(file_path, "Porozitatea",skip_rows=1)
    # print_dict_subset(porozitatea_dict)

    # # ------------------
    ph_dict, _ = read_excel_double_lvl(file_path, "pH",skip_rows=1)
    # print_dict_subset(ph_dict)

    # # ------------------
    rezerva_de_humus_dict, _ = read_excel_double_lvl(file_path, "Rezerva de humus",skip_rows=1)
    # print_dict_subset(rezeva_de_humus_dict)

    # # ------------------
    carb_dict, _ = read_excel_one_lvl(file_path, "Conținutul de carbonați")
    # print_dict_subset(carb_dict)



    # alunecari = "Absente"
    # panta = "10%<P≤15%"
    # temp?
    # precip?
    # salin_alcalin = "Slab salinizat/alcalizat"
    # glizare?
    # pseudoglizare = "Nepseudogleizat"
    # apre_freatice?
    # vol_edafil_util?
    # tetura?
    # ph = "pH≤3,5"
    # rezeva_de_humus?
    # carb = "CaCO3≤4"


    # porozitate?


    adanc_apa_texture_mapping_dict = {
        "Nisipoasă (≥90% 0,01mm+)" : "Grosieră",
        "Nisipo-lutoasă (≥80% 0,01mm+)" : "Grosieră",
        "Luto-nisipoasă (≥70% 0,01mm+)" : "Mijlocie",
        "Luto-argiloasă (≥35% 0,01mm+)" : "Mijlocie",
    }
    textura_argument_adanc_apa = adanc_apa_texture_mapping_dict.get(textura, "Fină")

    porozitate_textura_mapping_dict = {
        "75%>P≥70%" : "Soluri cu porozitate mică - mijlocie",
        "70%>P≥60%" : "Soluri cu porozitate mică - mijlocie",
        "60%>P" : "Soluri cu porozitate mică - mijlocie"
    }
    potozitate_argument_textura = porozitate_textura_mapping_dict.get(porozitatea, "Soluri cu porozitate normală - extrem de mare")

    textura_porozitate_mapping_dict = {
        "Nisipoasă (≥90% 0,01mm+)": "Soluri cu altă textură, decât fină",
        "Nisipo-lutoasă (≥80% 0,01mm+)": "Soluri cu altă textură, decât fină",
        "Luto-nisipoasă (≥70% 0,01mm+)": "Soluri cu altă textură, decât fină",
        "Lutoasă (≥55% 0,01mm+)": "Soluri cu altă textură, decât fină",
        "Sedimente cu >40% CaCO3": "Soluri cu altă textură, decât fină",
        "Roci compacte fisurate și pietrișuri": "Soluri cu altă textură, decât fină",
        "Roci compacte dure și impermeabile": "Soluri cu altă textură, decât fină"
    }
    textura_argument_potozitate = textura_porozitate_mapping_dict.get(textura, "Soluri cu textură fină")

    textura_humus_mapping_dict = {
        "Luto-nisipoasă (≥70% 0,01mm+)": "Soluri cu textură fină și mijlocie",
        "Lutoasă (≥55% 0,01mm+)": "Soluri cu textură fină și mijlocie",
        "Luto-argiloasă (≥35% 0,01mm+)": "Soluri cu textură fină și mijlocie",
        "Argiloasă (≥15% 0,01mm+)": "Soluri cu textură fină și mijlocie",
        "Argiloasă grea (<15% 0,01mm+)": "Soluri cu textură fină și mijlocie",
        "Depozite organice": "Soluri cu textură fină și mijlocie"
    }
    textura_argument_humus = textura_humus_mapping_dict.get(textura, "Soluri cu textură grosieră")

    drenaj_mapping_dict = {
        "Da": "Gradul de gleizare artificială",
        "Nu": "Gradul de gleizare naturală"
    }
    drenaj_desecare = drenaj_mapping_dict[drenaj_desecare]

    rez_dict = {}
    for c in culturi:
        rez_dict[c] = {}
        rez_dict[c]["alunecari"] = alunecari_dict.get(c, {}).get(alunecari, None)
        rez_dict[c]["panta"] = panta_dict.get(c, {}).get(panta, None)
        rez_dict[c]["salin_alcalin"] = salin_and_alc_dict.get(c, {}).get(salin_alcalin, None)
        rez_dict[c]["gleizare"] = gleuiz_dict.get(c, {}).get(drenaj_desecare, {}).get(gleizare, None)
        rez_dict[c]["pseoudoglizare"] = pseudogleiz_dict.get(c, {}).get(pseudogleizare, None)
        rez_dict[c]["adancirea_apelor_freatice"] = adanc_ap_freat_dict.get(c, {}).get(textura_argument_adanc_apa, {}).get(adancirea_apelor_freatice, None)
        rez_dict[c]["textura"] = textur_dict.get(c, {}).get(potozitate_argument_textura, {}).get(textura, None)
        rez_dict[c]["porozitate"] = porozitatea_dict.get(c, {}).get(textura_argument_potozitate, {}).get(porozitatea, None)
        rez_dict[c]["ph"] = ph_dict.get(c, {}).get(adancimea_sat, {}).get(ph, None)
        rez_dict[c]["rezerva_de_humus"] = rezerva_de_humus_dict.get(c, {}).get(textura_argument_humus, {}).get(rezerva_de_humus, None)
        rez_dict[c]["carbonati"] = carb_dict.get(c, {}).get(carb, None)    

    for cultura, valori in rez_dict.items():
        coeficienti = [v for v in valori.values() if isinstance(v, (int, float))]
        general = 1
        for c in coeficienti:
            general *= c
        
        rez_dict[cultura]["general"] = round(general,2)


    rez_dict = { full: rez_dict[short] for short, full in zip(culturi, culturi_full) }


    # print (rez_dict["PS"]["alunecari"]) 
    # print (rez_dict["PS"]["panta"]) 

    # for key, values in rez_dict.items():
    #     for col_name, col_value in values.items():
    #         print(key, col_name, col_value)

    return rez_dict



