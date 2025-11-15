import eel

eel.init("web")

@eel.expose
def calculeaza(panta, temperatura):
    return f"Rezultat: {panta}, {temperatura}°C"

eel.start("index.html", size=(500, 800))
