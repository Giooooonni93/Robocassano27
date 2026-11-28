"""Prova dell'ARDUINO CHE SI STACCA (FIX 151, scatola nera V62 26/11 16:39 da 142,97 s: "[Errno 5] Input/output error").

Un Arduino finto manda pacchetti veri (laser 83/99/23, switch acceso) per 0,5 s, poi la porta dà "[Errno 5]
Input/output error" a ogni lettura (come quando Linux perde il dispositivo USB). Dopo la riconnessione l'Arduino finto
torna a mandare pacchetti. Si guarda:
  - se i dati restano gli ULTIMI ricevuti (robot alla cieca) o vanno a zero con lo switch "spento" (motori fermi);
  - se il programma riapre la porta e i dati tornano;
  - cosa scrive StatoArduino() per la cabina (dalla V63).
Niente simulatore e niente hardware: si usa solo la classe Robot di ViennaClsRobot.py.

Uso: python3 prova_arduino_staccato.py <cartella versione>
"""
import os
import sys
import threading
import time
import types


class PortaFinta:
    def __init__(self, stato):
        self.stato = stato
        self.port = "/dev/ttyUSB0"

    @property
    def in_waiting(self):
        # come pyserial: "Input/output error" arriva già chiedendo quanti byte ci sono
        if self.stato["rotta"]:
            raise OSError(5, "Input/output error")
        time.sleep(0.01)
        return len(self._riga())

    def _riga(self):
        return b"83,99,23,123,-2,1,0,1,0,0\n"   # d1,d2,d3, hd,rl,pt, sw1 ("0" = acceso), sw2, t0,t1

    def read(self, n=1):
        if self.stato["rotta"]:
            raise OSError(5, "Input/output error")
        time.sleep(0.01)
        return self._riga()

    def readline(self):
        return self.read()

    def close(self):
        pass

    def reset_input_buffer(self):
        pass


def main():
    cartella = os.path.abspath(sys.argv[1])
    sys.path.insert(0, cartella)
    finto_serial = types.SimpleNamespace(SerialException=type("SerialException", (Exception,), {}),
                                         Serial=lambda *a, **k: None)
    sys.modules["serial"] = finto_serial
    sys.modules.setdefault("smbus2", types.SimpleNamespace(SMBus=lambda *a, **k: None))
    import ViennaClsRobot as VR
    stato = {"rotta": False}
    r = VR.Robot.__new__(VR.Robot)
    r.__dict__.update(dict(running=True, _lock=threading.Lock(), _camp_lock=threading.Lock(), _serial_buffer="",
                           _last_distances=(0, 0, 0), _last_imu=(0, 0, 0), _last_switch=(False, False),
                           _last_tilt=(0, 0), _last_packet_time=time.time(), _storia_becc=[]))
    for nome in ("_ard_pacchetti", "_ard_riconnessioni"):
        setattr(r, nome, 0)
    r._ard_pps = [time.time(), 0, 0.0]
    r._ard_errori = []
    r._hd_correzione, r._hd_prec, r._salti_bussola, r._salto_avviso_t = 0, None, 0, 0.0
    r._campiona = lambda: None
    riaperture = []

    def init_finto(port=None):
        riaperture.append(time.time())
        stato["rotta"] = False                       # l'Arduino ricompare
        r.arduino = PortaFinta(stato)
        threading.Thread(target=r._arduino_reader, daemon=True).start()
    r._init_arduino = init_finto
    r.arduino = PortaFinta(stato)
    threading.Thread(target=r._arduino_reader, daemon=True).start()

    def foto(quando):
        with r._lock:
            d, sw = r._last_distances, r._last_switch
        info = r.StatoArduino() if hasattr(r, "StatoArduino") else "-"
        print(f"  {quando:28s} laser {d}  switch acceso {sw[1]}  StatoArduino {info}")

    time.sleep(0.5)
    foto("Arduino che funziona")
    stato["rotta"] = True
    t0 = time.time()
    time.sleep(0.6)
    foto("0,6 s dopo l'errore")
    time.sleep(1.4)
    foto("2 s dopo l'errore")
    print(f"  porta riaperta: {'SI, dopo %.1f s' % (riaperture[0] - t0) if riaperture else 'NO'}")
    r.running = False


if __name__ == "__main__":
    main()
