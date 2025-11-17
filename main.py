import eel
from helpers import return_note_de_bonitare_dict, print_dict_subset

eel.init("web")

@eel.expose
def calc_note_de_bonitare_dict(data):
    print("Primite din JS:")
    data['carb'] = data['carb'].replace(" ", "")
    data['edafic'] = data['edafic'].replace(" ", "")
    data['humus'] = data['humus'].replace(" ", "")
    data['panta'] = data['panta'].replace(" ", "")
    data['ph'] = data['ph'].replace(" ", "").replace(".",",")
    data['carb'] = data['carb'].replace(" ", "")
    data['porozitate'] = data['porozitate'].replace(" ", "")
    print_dict_subset(data, 100)

    # Aici poți calcula nota de bonitare
    # ...
    # Întoarce dictul final
    rez_dict = return_note_de_bonitare_dict(alunecari=data['alunecari'],
                                        panta=data['panta'],
                                        salin_alcalin=data['salinizare'],
                                        gleizare=data['gleizare'],
                                        pseudogleizare=data['pseudogleizare'],
                                        adancirea_apelor_freatice=data['apa_freatica'],
                                        textura=data['textura'],
                                        porozitatea=data['porozitate'],
                                        ph=data['ph'],
                                        carb=data['carb'],
                                        rezerva_de_humus=data['humus'],
                                        drenaj_desecare=data['drenaj'],
                                        adancimea_sat=data['saturatie'])
    
    rez_dict = {key[4:-1]: value for key, value in rez_dict.items()}

    print("\nExtrase din data.xlsx:")
    print_dict_subset(rez_dict, 1)

    return rez_dict

eel.start("index.html", size=(500, 800))

