"""Prova dell'USCITA IN DISCESA (FIX 150, scatola nera V61 26/11 14:57, 489 s).

Sul robot vero, passata la porta dell'uscita, il muso scende nella discesa fuori dall'arena (beccheggio fino a -26) e il
laser davanti, inclinato, passa da 30 a 50 cm: il controllo "non avanzo (tocco lo stipite)" faceva tornare il robot
dentro l'arena. Qui, dopo "E' l'USCITA: esco", quando il robot si è spostato di 18 cm, per 2 s il simulatore fa leggere
al robot beccheggio -20 e laser davanti 50 cm. Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_uscita_discesa.py <cartella versione> [scenario, es. arena] [semi, es. 1,2]
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
st = {"da": None, "t0": None, "n_log": 0, "fatto": False}
sens_vero = mondo.Mondo.aggiorna_sensori_robot
def aggiorna(self):
    sens_vero(self)
    r = getattr(self, "robot", None)
    if r is None or st["fatto"]:
        return
    nuovi = self.log[st["n_log"]:]
    st["n_log"] = len(self.log)
    if st["da"] is None and any("USCITA: esco" in m for _, m in nuovi):
        st["da"] = (self.x, self.y)
    if st["da"] is not None and st["t0"] is None and math.hypot(self.x - st["da"][0], self.y - st["da"][1]) >= 18:
        st["t0"] = self.t
        self.evento("info", "PROVA: discesa fuori dalla porta (beccheggio -20, laser davanti 50 cm)")
    if st["t0"] is not None:
        if self.t - st["t0"] > 2.0:
            st["fatto"] = True
            return
        with r._lock:
            _, rl, hd = r._last_imu
            r._last_imu = (-20, rl, hd)
            d = r._last_distances
            r._last_distances = (d[0], 50, d[2])
mondo.Mondo.aggiorna_sensori_robot = aggiorna
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[5])}, sys.argv[4])
chiavi = ("USCITA", "Uscita", "Uscito", "uscito", "muso scende", "non avanzo")
righe = [f"{t:6.1f} {m[:110]}" for t, m in r["log"] if any(k in m for k in chiavi)]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:10]}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    scenario = sys.argv[2] if len(sys.argv) > 2 else "arena"
    semi = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "1").split(",")]
    nome_v = os.path.basename(cartella)
    for seme in semi:
        nome = f"uscita_discesa_{nome_v}_{scenario}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, str(seme)],
                             capture_output=True, text=True, cwd=QUI, timeout=900)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        print(f"{nome_v} ({scenario}, seme {seme}): {r['fine']} dopo {r['durata']:.0f} s")
        for x in r["righe"]:
            print("     ", x)


if __name__ == "__main__":
    main()
