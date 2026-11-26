"""Prova della SCATOLA DELL'OSTACOLO PRESA PER L'INGRESSO (FIX 147, scatole nere 26/11 V60 12:53 a 118 s e 12:58 a
50,8 s; V58 24/11 11:05 a 133,8 e 227,7 s).

Sul robot vero l'ostacolo è una scatola di cartone: a 10-15 cm la camera linea la vede in alto nell'immagine e YOLO dice
"In" (argento) 0,93-0,95; il robot cercava la porta e poi "Sono entrato nell'arena" in mezzo alla pista.
Qui, pista `gara`: quando il robot è vicino all'ostacolo con il laser davanti sotto 16 cm, il simulatore colora di
marrone cartone il terzo alto dell'immagine della camera linea e fa dire a YOLO "In" in quella zona.
Si guarda se il robot entra in una finta arena o aggira l'ostacolo. Il simulatore non si tocca.

Uso: python3 prova_scatola_argento.py <cartella versione> [semi, es. 1,2]
"""
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SIM = max((os.path.join(QUI, "..", d) for d in os.listdir(os.path.join(QUI, ".."))
           if d.startswith("ClaudeRob_Simulatore_V")), key=lambda d: int(d.rsplit("_V", 1)[1]))

GARA = r'''
import sys, json, math
sys.path.insert(0, sys.argv[1])
import mondo, esegui

def scatola_davanti(self):
    o = self.C.get("ostacolo")
    if not o:
        return False
    cx, cy = o["x"] + o["w"] / 2, o["y"] + o["h"] / 2
    return math.hypot(self.x - cx, self.y - cy) < 30 and 0 < self.tof_val[1] < 16

img_vera = mondo.Mondo.immagine_linea
def immagine(self, pose=None):
    img = img_vera(self, pose)
    if scatola_davanti(self):
        img = img.copy()
        img[: img.shape[0] // 3] = (120, 170, 200, 255)[:img.shape[2]]   # cartone (BGR)
    return img
mondo.Mondo.immagine_linea = immagine

yolo_vero = mondo.Mondo.yolo_cross_linea
def yolo(self, img224):
    out = yolo_vero(self, img224)
    if scatola_davanti(self):
        self.yolo_vista = "In"
        return [(mondo.CLASSI_CROSS["In"], 0.95, (0.0, 0.0, 223.0, 74.0))] + out
    return out
mondo.Mondo.yolo_cross_linea = yolo

r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[4])}, "gara")
chiavi = ("Striscia argento", "Ingresso", "Sono entrato", "OSTACOLO", "AVVIO ARENA", "ANNULLATO")
righe = [f"{t:6.1f} {m[:120]}" for t, m in r["log"] if any(k in m for k in chiavi)]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:12]}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    semi = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "1").split(",")]
    nome_v = os.path.basename(cartella)
    for seme in semi:
        nome = f"scatola_argento_{nome_v}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, str(seme)],
                             capture_output=True, text=True, cwd=QUI, timeout=900)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        print(f"{nome_v} (seme {seme}): {r['fine']} dopo {r['durata']:.0f} s")
        for x in r["righe"]:
            print("     ", x)


if __name__ == "__main__":
    main()
