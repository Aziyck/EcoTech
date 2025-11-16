from helpers import read_excel_one_lvl, print_dict_subset, read_excel_double_lvl, read_temp_tabl, read_culturi_values, return_note_de_bonitare_dict

file_path = "data.xlsx"

culturi, _ = read_culturi_values(file_path, "Sheet1")
# print(culturi)

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
# gleuiz_dict, _ = read_excel_double_lvl(file_path, "Gleizarea")
# print_dict_subset(gleuiz_dict)

# # ------------------
pseudogleiz_dict, _ = read_excel_one_lvl(file_path, "Pseudogleizare")
# print_dict_subset(pseudogleiz_dict)

# # ------------------
# adanc_ap_freat_dict, _ = read_excel_double_lvl(file_path, "Adâncimea apelor freatice", drop_empty_columns=True)
# print_dict_subset(adanc_ap_freat_dict)

# # ------------------
# textur_dict, _ = read_excel_double_lvl(file_path, "Textura",skip_rows=1)
# print_dict_subset(textur_dict)

# # ------------------
# vol_edafil_util_dict, _ = read_excel_double_lvl(file_path, "Volumul edafic util",skip_rows=1)
# print_dict_subset(vol_edafil_util_dict)

# # ------------------
# porozitatea_dict, _ = read_excel_double_lvl(file_path, "Porozitatea",skip_rows=1)
# print_dict_subset(porozitatea_dict)

# # ------------------
ph_dict, _ = read_excel_double_lvl(file_path, "pH",skip_rows=1)
# print_dict_subset(ph_dict)

# # ------------------
# rezeva_de_humus_dict, _ = read_excel_double_lvl(file_path, "Rezerva de humus",skip_rows=1)
# print_dict_subset(rezeva_de_humus_dict)

# # ------------------
carb_dict, _ = read_excel_one_lvl(file_path, "Conținutul de carbonați")
# print_dict_subset(carb_dict)

adancimea_sat = "Soluri cu grad de saturație în primii 20 de cm sau în Ap>55%"

alunecari = "Absente"
panta = "P≤5%"
# temp?
# precip?
salin_alcalin = "Slab salinizat/alcalizat"
# glizare?
pseudoglizare = "Nepseudogleizat"
# apre_freatice?
# vol_edafil_util?
# tetura?
ph = "pH≤3,5"
# rezeva_de_humus?
carb = "CaCO3≤4"


# porozitate?

rez_dict = {}
for c in culturi:
    rez_dict[c] = {}
    rez_dict[c]["alunecari"] = alunecari_dict.get(c, {}).get(alunecari, None)
    rez_dict[c]["panta"] = panta_dict.get(c, {}).get(panta, None)
    rez_dict[c]["salin_alcalin"] = salin_and_alc_dict.get(c, {}).get(salin_alcalin, None)
    rez_dict[c]["pseoudoglizare"] = pseudogleiz_dict.get(c, {}).get(pseudoglizare, None)
    rez_dict[c]["ph"] = ph_dict.get(c, {}).get(adancimea_sat, {}).get(ph, None)
    rez_dict[c]["carb"] = carb_dict.get(c, {}).get(carb, None)    

for cultura, valori in rez_dict.items():
    coeficienti = [v for v in valori.values() if isinstance(v, (int, float))]
    general = 1
    for c in coeficienti:
        general *= c
    
    rez_dict[cultura]["general"] = general

# print (rez_dict["PS"]["alunecari"]) 
# print (rez_dict["PS"]["panta"]) 

# for key, values in rez_dict.items():
#     for col_name, col_value in values.items():
#         print(key, col_name, col_value)

print_dict_subset(return_note_de_bonitare_dict(), 30)



