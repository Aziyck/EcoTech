import eel
from helpers import return_note_de_bonitare_dict

eel.init("web")

@eel.expose
def calculeaza(panta, temperatura):
    return f"Rezultat: {panta}, {temperatura}°C"

@eel.expose
def calc_note_de_bonitare_dict(data):
    print("Primite din JS:")
    data['carb'] = data['carb'].replace(" ", "")
    data['edafic'] = data['edafic'].replace(" ", "")
    data['humus'] = data['humus'].replace(" ", "")
    data['panta'] = data['panta'].replace(" ", "")
    data['ph'] = data['ph'].replace(" ", "").replace(".",",")
    data['carb'] = data['carb'].replace(" ", "")
    data['porozitateb'] = data['porozitate'].replace(" ", "")
    print(data)

    # Aici poți calcula nota de bonitare
    # ...
    # Întoarce dictul final
    rez_dict = return_note_de_bonitare_dict(alunecari=data['alunecari'],
                                        panta=data['panta'],
                                        salin_alcalin=data['salinizare'],
                                        pseudogleizare=data['pseudogleizare'],
                                        ph=data['ph'],
                                        carb=data['carb'])
    print(rez_dict)

    return rez_dict

eel.start("index.html", size=(500, 800))

