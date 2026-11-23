# Strumenti di prova di Claude (V35-V39)

Script usati per provare le porte e l'altalena nel simulatore (dal 10/11 il Simulatore V32). Stanno in `02_Robotica/Strumenti_prove_Claude/` e trovano
da soli il simulatore in `../ClaudeRob_Simulatore_V32` (oppure nella variabile d'ambiente `SIMULATORE`). Si lanciano da questa
cartella. Le copie di prova delle versioni finiscono in `copie_di_prova/` (si possono cancellare); i replay nel simulatore.

| Script | Cosa prova | Risultato V39 |
|---|---|---|
| `gira.py` | una gara intera con riassunto | scuola semi 1-6 arrivo; rcj2026 1468, lunga 1893, contorto 1989 |
| `prova_ingresso.py` | porta d'ingresso con il robot spostato (y 55-95) e lato previsto | 8/8 col lato giusto, 6/8 col lato sbagliato |
| `prova_uscita.py` | porta d'uscita con il robot spostato (-12..+12 cm) | 9/9 |
| `prova_uscita_angolo.py` | uscita vista seguendo il muro, davanti al muro accanto alla porta (x 222-234) | 4/4 |
| `prova_altalena.py` | riconoscimento dell'altalena con uno stoppie finto | "PROBABILE ALTALENA SUPERATA", riparte |
| `prova_verde_discesa.py` | (13/11, FIX 115; dal 16/11 anche `salita`, FIX 118) incrocio a + coi verdi in diagonale in fondo a una discesa di 21 gradi; misura dove sono le ruote quando il robot comincia a girare | V48: 17,5 cm prima del centro; V50: 0-0,5 cm, svolta a sinistra |
| `prova_switch_disturbo.py` | (16/11, FIX 117) switch spento per 0,15 s durante la gara | V50: salta all'arena e si blocca; V51: "era un disturbo, continuo" |
| `prova_pallina_bordo.py` | (16/11, FIX 119) vicino alla pallina il robot viene ruotato di 25 gradi: pallina tagliata dal bordo | "Pallina tagliata dal bordo": si gira e la riguarda |
| `prova_rotonda.py` | (16/11 e 23/11, FIX 124/135) rampa di 21 gradi e la rotonda della scuola in cima (dalla foto), verdi a destra; `lenta`: in salita il robot quasi si ferma, come quello vero | Esce a destra dalla rotonda; `lenta` V56 0/6, V57 3/3 |
| `prova_ruote_davanti.py` | (16/11 e 23/11, FIX 125/129/136) il simulatore tiene il robot sul muso (-65 gradi) finché non dà il colpetto; 4° argomento: laser davanti (5, 0, 40 cm); 5° `avanti`: si libera solo con un colpetto in avanti | V53: colpetto solo con 5 cm; V54: con 5, 0 e 40 cm; `avanti`: V56 resta così, V57 si libera |
| `prova_linea_rossa.py` | (16/11, FIX 127/128) dove si ferma il robot rispetto alla linea rossa; con `lop` lo switch si spegne 7 s dopo l'uscita dall'arena | V53: rossa 16-17 cm davanti al centro (davanti al muso), con `lop` tempo scaduto; V54: 1-2 cm dal centro, arrivo |
| `prova_nera_scambiata.py` | (19/11 e 23/11, FIX 130-133, 139; `lop_uscita`: LoP mentre cerca l'uscita) YOLO vede la nera come argento (la foto resta vera); `lop`: LoP dentro l'arena (rcj2026); `inganno_lop`: anche la foto inganna, la nera va nel verde, poi LoP poco fuori dall'arena (900 s) | V54: resta in arena; V55: 3 palline giuste; `inganno_lop` V55 dietrofront e 3 LoP, V56 rientra e rifà l'arena |
| `prova_oscillazione.py` | (23/11, FIX 141) per 15 s il seguilinea "vede" quello che vedeva il robot vero nell'angolo del quadrato (spinta a destra / correzione a sinistra) | V57 nessuna reazione; V58 dopo 4 s "sterzo a destra e a sinistra... passo l'angolo" |
| `analizza_scatola_nera.py` | eventi di una scatola nera vera, o i campioni tra due istanti | – |
| `terminale_nuovo.py` | **moviola**: rivede una scatola nera vera nel terminale con la cabina di pilotaggio della V42 (camere, cronometro, fasi). Finestra di almeno 100 x 38 | – |

Esempi:
```
python gira.py ../ClaudeRob_V39 prova scuola 480 seme=3
python prova_ingresso.py ../ClaudeRob_V39 ing_95 95 -1
python prova_uscita.py ../ClaudeRob_V39 usc_10 10
python prova_uscita_angolo.py ../ClaudeRob_V39 ang_230 230
python prova_altalena.py ../ClaudeRob_V39 alt
python -I analizza_scatola_nera.py ../ScatoleNere/run_2026-11-06_10-48-52_V38.jsonl
python3 -I terminale_nuovo.py ../ScatoleNere/run_2026-11-09_10-46-10_V40.jsonl --da 120 --velocita 2
python ../ClaudeRob_Simulatore_V32/crea_replay.py confronto.html <replay_A.json>:"A" <replay_B.json>:"B"
```
