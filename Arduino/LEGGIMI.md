# Arduino Nano del robot (laser, giroscopio, switch)

L'Arduino legge i 3 laser VL53L1X, il giroscopio BNO055 e i 2 switch, e manda al Raspberry 20 righe al secondo
(230400 baud) con 10 valori:

```
laser1,laser2,laser3,rotta,rollio,beccheggio,switch1,switch2,(9o valore),(10o valore)
```

| Cartella | Cosa è |
|---|---|
| `InoSensorRobusto/` | lo sketch del 21/10, così come il prof l'ha mandato il 28/11 ("dovrebbe essere questo") |
| `InoSensorRobusto2/` | la versione nuova del 28/11: stessa riga di 10 valori, il Raspberry non va cambiato |

## Cosa c'è di nuovo in InoSensorRobusto2 (segnato nel codice con `[ARDUINO n]`)

1. **Giroscopio bloccato.** Nelle scatole nere (16/11, 26/11 16:45) il giroscopio a volte legge sempre (-2, -2, 0): è
   il BNO055 che risponde tutti zeri. Prima lo sketch lo credeva vivo. Ora: 0,0,0 esatti per mezzo secondo = bloccato,
   si riavvia (ci mette quasi 1 s: in quel momento il Raspberry vede "ARDUINO ZITTO" e il robot si ferma).
2. **Laser fermo.** Un laser che non dà misure nuove per 1 s: si riavviano solo i laser, al massimo una volta ogni 10 s.
3. **Diagnosi.** Il 9o valore (prima "urto leggero", sempre 0) dice quante volte i sensori sono ripartiti
   dall'accensione. Nella scatola nera è il primo numero del campo `tilt`.
4. **Watchdog** (la Nano si riavvia da sola se si blocca per 1 s): spento come prima (`USA_WATCHDOG 0`). Si può
   accendere solo con il bootloader nuovo, vedi sotto.

Quello che c'era già dal 21/10 resta:
- tempo massimo di 25 ms su ogni comunicazione I2C;
- laser che non aspettano;
- nessun `while(1)`;
- sensori rimessi in piedi se l'I2C si inchioda.

## Prima di caricarlo: quale sketch c'è adesso sulla Nano?

Questo sketch manda le righe **sempre**, anche con lo switch spento. Nelle scatole nere invece, quando si spegne lo
switch, l'Arduino **tace** ("Arduino zitto: switch spento?"). Quindi forse sulla Nano c'è un altro sketch. Per saperlo:

1. chiudete il programma del robot (un solo programma alla volta può usare la porta);
2. dal Raspberry: `python3 -m serial.tools.miniterm /dev/ttyUSB0 230400` (per uscire: Ctrl + ]);
3. spegnete lo switch: se le righe **continuano**, sulla Nano c'è InoSensorRobusto; se **si fermano**, c'è un altro
   sketch. Ditelo a Claude: il Raspberry conta sul fatto che con lo switch spento arrivino `0` sullo switch, quindi
   con InoSensorRobusto2 la LoP funziona lo stesso.

## Come caricarlo

1. IDE di Arduino, apri `InoSensorRobusto2/InoSensorRobusto2.ino` (la cartella deve avere lo stesso nome del file).
2. Librerie (Strumenti > Gestisci librerie): **VL53L1X** (Pololu), **Adafruit BNO055**, **Adafruit Unified Sensor**.
3. Scheda: Arduino Nano. Strumenti > Processore: prima **ATmega328P**; se il caricamento non va, **ATmega328P (Old
   Bootloader)**. Segnatevi quale funziona.
4. Premete **Verifica** (✓): deve dire "Compilazione terminata". Poi **Carica**.
5. Monitor seriale a **230400** baud: deve scrivere `READY` e poi 20 righe al secondo di 10 numeri.

## Il watchdog

Si può mettere `#define USA_WATCHDOG 1` **solo** se al punto 3 ha funzionato "ATmega328P" (bootloader nuovo). Con il
bootloader vecchio la Nano può ripartire all'infinito: si vede solo `READY` ripetuto o niente. In quel caso si ricarica
con `0` e non succede niente di grave.

## Se l'Arduino si stacca ("Input/output error")

Quello non è lo sketch: è il collegamento USB che sparisce. Subito dopo, sul Raspberry:

```
dmesg | grep -i -E "usb|ttyUSB|voltage" | tail -20
```

- `disconnect` → cavo USB (corto, fissato, lontano dai fili dei servo) o connettore lento;
- `under-voltage` → alimentazione: quando i servo tirano corrente la tensione cala.

Dalla V63 il programma del robot si accorge, ferma i motori e riapre la porta da solo (in cabina "ARDUINO STACCATO" e
poi "(riconnesso 1x)").
