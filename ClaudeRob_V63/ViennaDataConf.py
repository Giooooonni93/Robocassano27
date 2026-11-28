
#####   PID SeguiLinea   ####
# [FIX 4] Prima Kp veniva applicato DUE volte (err_PID*Kp), quindi il guadagno
# reale era Kp*Kp = 1.1*1.1 = 1.21 e Ki reale = 0.01*1.1 = 0.011.
# Ora Kp si applica una volta sola: per mantenere la stessa "forza" di prima
# usiamo direttamente i valori equivalenti. Il termine D aveva il segno
# sbagliato ed è stato corretto: RITARARE Kd IN CAMPO (partire da 0.05).
Kp=1.21
Ki=0.011
Kd=0.05
IntegrMax=1000      # [FIX 4] anti-windup: limite dell'integrale (Ki*IntegrMax = contributo massimo 11)

####   PID rotazioni/Dritto (prima erano scritti fissi dentro ViennaClsRobot.py)
PidGiroKp=1.8
PidGiroKi=0.05
PidGiroKd=0.4

####   VELOCITA' Movimenti  ####
Vel=57
VelCrs=47
VelArena=68
Alfa=0.4

####   VELOCITA' e Precisione Girate

VelMaxGiro=35
ErrMaxGiro=5
TimeoutGira=8.0     # [FIX 8] secondi massimi per una rotazione (se il robot è incastrato non gira all'infinito).
                    # Prima era 4 s: sul robot vero un dietrofront (Gira 170) può durare di più e veniva
                    # interrotto a metà. Se nel terminale compare "[Gira] TIMEOUT" alzate ancora questo valore.

### Variazioni Velocità e Correzione

AlfaVelSal = 0.6
AlfaVelDis = 0.4
AlfaCrosSal = 0.3
AlfaCrosDis = 0.3
AlfaCorSal = 0.5
AlfaCorDis = 0.5

### Costanti Immagine
SogMask=100
# [FIX 30] gradi di rotazione per ogni pixel di scarto nell'immagine 224x224 della camera arena.
# 0,3 = campo visivo di circa 66 gradi diviso 224 pixel. Misuratelo: mettete una pallina di lato,
# leggete centro_x e l'angolo vero, e calcolate gradi / (centro_x - 112).
GradiPerPixelArena = 0.3
# [FIX 33] secondi di avanzamento dritto dopo aver confermato la striscia argento dell'ingresso:
# devono bastare a portare TUTTO il robot dentro l'arena (circa 25 cm). Regolatelo in campo.
TempoEntrataArena = 2.5     # [FIX 68] prima 1.2. Servono circa 29 cm: dal muso alla striscia (~4 cm) + robot lungo
                            # 21,5 cm + margine. 1,2 s andava bene a 24 cm/s, ma la scatola nera del 23/10 dice che
                            # il robot va a circa 11 cm/s: entrava di soli 13-14 cm e restava con il retro fuori.
# [FIX 34] uscita dalla porta dell'arena
DistanzaLiberoPorta = 35    # cm: se il laser frontale legge più di così, davanti c'è l'apertura
# [FIX 48] Il VL53L0X manda 0 quando NON vede niente entro la sua portata (circa 1,2 m): per esempio
# quando guarda fuori da una porta. Nelle funzioni dell'uscita lo 0 ora vale LASER_LONTANO (= lontano),
# non "muro attaccato". Se però Arduino non risponde (tutto a 0 per più di 0,3 s) resta 0.
LASER_LONTANO = 150         # cm
AvvicinamentoPorta = 30     # [FIX 48] cm che il robot percorre verso la porta guardando il pavimento
PassiMaxPorta = 40          # passi da 0,1 s scorrendo lungo la parete prima di rinunciare
TempoCentroPorta = 0.9      # s di avanzamento dopo che il laser laterale vede l'apertura, per centrarsi
                            # [FIX 40] il laser laterale è 10 cm dietro il muso (1,5 cm davanti al centro
                            # delle ruote): per arrivare a metà di una porta da 27 cm servono circa 15 cm
TempoUscitaPorta = 2.5      # s di avanzamento dritto per uscire del tutto dall'arena ([FIX 68] prima 1.5,
                            # stesso motivo di TempoEntrataArena: a 11 cm/s erano solo 16 cm)
# [FIX 35] centratura sulla porta prima di uscire (camera arena + laser frontale)
TempoIndietroPorta = 1.0    # s di retromarcia davanti alla porta: da lontano la camera la vede tutta
LarghezzaPorta = 27         # cm: [FIX 40] MISURATA sul vostro campo (ingresso e uscita)
                            # NB: la centratura usa anche GradiPerPixelArena: tarate quello (vedi sopra)
TolleranzaPorta = 3         # cm: se sono spostato meno di così non correggo
LaserMaxAffidabile = 120    # cm: oltre questa lettura il VL53L0X non è affidabile, uso il tempo
VelocitaArenaCmS = 10       # cm/s a VelArena*0.7. [FIX 67] prima 17: la scatola nera del 23/10 (laser frontale
                            # che si avvicina al muro) dice circa 10 cm/s, e quasi uguale a velocità 34, 47 o 68
                            # (i servo arrivano subito al massimo). Cronometrate 1 metro e correggete.
DistanzaCameraArena = 10.5  # cm tra il centro delle ruote e la camera arena ([FIX 40] muso a 11,5 cm, camera 1 cm dietro)

# [FIX 38] uscita dall'arena seguendo i muri (quando la camera scambia l'ingresso per l'uscita)
TempoMaxRicercaPorta = 45   # s di ricerca con la camera prima di passare al giro dei muri
TempoMaxPerimetro = 70      # s massimi di giro dei muri

### [FIX 53] USCITA COSTEGGIANDO LE PARETI (metodo proposto dalla squadra il 22/10)
# Dopo l'ultima pallina il robot sceglie il lato con la parete più vicina, la costeggia tenendo il fianco
# a LATO_MURO_CM e, quando il laser laterale "cade" in un'apertura, la misura, torna indietro fino al centro,
# si gira e guarda con la camera arena (e con la camera linea il pavimento) se è l'uscita o l'ingresso.
USCITA_MODO = "muri"        # "muri" = questo metodo; "camera" = come prima (camera arena, poi giro dei muri)
LATO_MURO_CM = 6.5          # cm tra il fianco del robot e la parete. [FIX 63] prima 5: idea della squadra
                            # (23/10) tenerla a 6-7 cm. Con 5 cm il robot non ha spazio per girarsi negli angoli
                            # (dal centro delle ruote allo spigolo ci sono circa 14 cm, al fianco 7,8)
APERTURA_CM = 15            # il laser laterale legge più di così, tutto d'un colpo: c'è un'apertura
ANGOLO_CM = 8               # laser frontale sotto questa distanza: angolo o triangolo, giro di 90 gradi
INDIETRO_CAMERA_S = 0.8     # s di retromarcia davanti all'apertura per guardarla con la camera arena
TEMPO_MAX_MURI = 150
### [FIX 63] GIRO DEI MURI A DISTANZA COSTANTE (scatola nera del 23/10: voleva 5 cm, stava a 10-30 cm)
PARETE_KP = 3.0             # gradi di inclinazione verso il muro per ogni cm di errore sulla distanza
PARETE_ANGOLO_MAX = 25      # gradi massimi di inclinazione verso (o via da) il muro
PARETE_ERR_RUOTA = 7        # gradi: se il robot è storto più di così si raddrizza ruotando sul posto
                            # [FIX 94] prima 4: si fermava a ruotare di continuo (05/11: 46 cm in 15 s)
PARETE_TOLL_RUOTA = 3       # [FIX 94] gradi di tolleranza di quelle rotazioni (prima 1,5)
PARETE_PASSO_S = 0.2        # s di avanzamento dritto tra un controllo e l'altro ([FIX 94] prima 0,12)
PARETE_VOLUTA_PASSO = 10    # [FIX 94] gradi massimi di cambio della direzione voluta per passo (prima 8)
PARETE_ANTICIPO_CM = 25     # [FIX 94] laser frontale sotto questa distanza: comincio a staccarmi dal muro...
PARETE_ANTICIPO_LATO = 6    # ...fino a LATO_MURO_CM + tanti cm quando arriva a ANGOLO_CM (poi la svolta di 90 come prima)
FERMO_DOPO_ARRIVO = True    # [FIX 95] arena fatta + linea rossa: il robot resta fermo fino allo spegnimento dello switch
AVANZA_ARRIVO_S = 1.0       # [FIX 95] s di avanzamento dopo aver visto la linea rossa, prima di fermarsi del tutto (~10 cm)
PARETE_STIMA = True         # stima la direzione VERA del muro da come cambia il laser laterale avanzando
                            # (se il giroscopio o la direzione d'ingresso sono sbagliati di qualche grado)
PARETE_STIMA_MAX = 30       # gradi massimi di correzione della direzione dei muri
PORTA_ANGOLO_CM = 4         # [FIX 70] porta che arriva fino all'angolo: il robot si ferma a tanti cm dal muro davanti
                            # (centro a ~15 cm dall'angolo, in mezzo alla porta, con lo spazio per girarsi)
PORTA_LATO_CM = 9.5         # [FIX 69] trovata l'uscita nel muro davanti, prima di uscire si mette con il fianco a
                            # tanti cm dal muro che stava seguendo: passa sia se la porta comincia nell'angolo sia se
                            # comincia 8 cm più in là (arena della scuola)
PARETE_MAX_INCLINAZIONE = 8 # [FIX 65] gradi di pitch/roll: in arena il pavimento è piano, se il giroscopio
                            # vede di più il robot sta salendo su qualcosa (pallina, bordo del triangolo)

### [FIX 64] ROTAZIONI E DRITTO
DRITTO_RUOTA_GRADI = 6      # in Dritto, se il robot è storto più di così si raddrizza ruotando sul posto
                            # (0 = come prima). Le correzioni di sterzo piccole non fanno girare i servo.
VelRuota = 47               # velocità delle rotazioni sul posto brevi (RuotaVerso)
### [FIX 72] ROTAZIONI PRECISE: il giroscopio vede la rotazione 0,2 s dopo il comando e il robot, fermati i
### motori, gira ancora di 5-7 gradi (scatole nere 23 e 26/10)
GIRA_ANTICIPO_S = 0.17      # Gira si ferma quando mancano (velocità di rotazione x 0,17 s) gradi: il resto lo fa
                            # il robot da solo mentre rallenta
INGRESSO_STRISCIA_CM = 25   # [FIX 71] lunghezza della striscia argento dell'ingresso (regolamento: 25 cm)
INGRESSO_TOLLERANZA_CM = 3  # [FIX 71] fuori centro di meno di così: si entra senza spostarsi
INGRESSO_AGGANCIO_GRADI = 40   # [FIX 96] la direzione d'ingresso si aggancia al lato delle piastrelle più vicino
                            # se dista meno di così (prima 25: con 26 gradi di errore il robot entrava storto)
ROBOT_LARGHEZZA_CM = 15.6   # [FIX 96] larghezza del robot (per i commenti: porta ~28 cm, restano ~6 cm per lato)
ENTRATA_TENTATIVI = 5       # [FIX 101] prima 3. [FIX 96] quante volte riprovare la porta se un fianco resta agganciato allo stipite
ENTRATA_SPOSTA_CM = 4.0     # [FIX 101] prima 3: si prova a +4, +8, poi -4, -8 cm. [FIX 96] di quanto spostarsi di lato (lontano dallo stipite) prima di riprovare
ENTRATA_STORTO_GRADI = 8    # [FIX 96] nella porta: se il robot si gira da solo di più di così, un fianco è agganciato
ENTRATA_AVANZO_MIN_CM = 1.5 # [FIX 96] nella porta: se in 0,6 s il laser davanti si accorcia meno di così, non avanzo
ENTRATA_LONTANO_CM = 60     # [FIX 106] laser davanti da qui in su (porta aperta): a ~1 m balla di +-2 cm, controllo più lento
ENTRATA_LONTANO_ATTESA_S = 1.5  # [FIX 106] con davanti lontano, "non avanzo" si controlla solo dopo tanti secondi
ENTRATA_LONTANO_AVANZO_CM = 5.0 # [FIX 106] ... e vuole che in 1,2-1,5 s il laser si sia accorciato almeno di tanto
ENTRATA_STERZO_MIN = 45     # [FIX 96] nella porta lo sterzo corregge almeno con questo valore (sotto ~40 i servo non girano)
CAM_LINEA_AVANTI = 12.0     # [FIX 71] camera linea: cm davanti al centro delle ruote (misure del robot, come nel
CAM_LINEA_ALTEZZA = 8.3     #          simulatore): altezza dal pavimento in cm,
CAM_LINEA_INCLINAZIONE = 15.0   #      gradi in avanti rispetto alla verticale,
CAM_LINEA_HFOV = 80.0       #          gradi di campo visivo orizzontale
ARGENTO_RECENTE_S = 4       # [FIX 75] se la linea finisce entro tanti secondi da quando YOLO ha visto l'argento,
                            # si riprova l'ingresso invece di cercare la linea
RICERCA_A_SCATTI = True     # [FIX 76] ricerca delle palline a scatti fermi con giro completo (False = come prima)
RICERCA_PASSO_GRADI = 30    # [FIX 76] gradi di ogni scatto
SVOLTA_INGRESSO_S = 6       # [FIX 71] se l'argento arriva entro tanti secondi da una svolta a un incrocio, si entra
                            # nella direzione "prima della svolta + 90 gradi"
RUOTA_ANTICIPO = 12         # gradi: sotto questo errore niente più rotazione continua, ma colpi brevi
RUOTA_ASSESTA_S = 0.25      # s di attesa dopo la rotazione continua, per leggere dove è arrivato davvero
RUOTA_PAUSA_S = 0.2         # s di attesa dopo ogni colpo
RUOTA_COLPO_S_GRADO = 0.008 # durata del colpo: 0,008 s per ogni grado che manca (da 0,03 a 0,12 s)
### [FIX 65] GIROSCOPIO COME SENSORE DI TOCCO
BLOCCO_S = 0.6              # s: se il robot deve ruotare ma per tutto questo tempo la direzione cambia
BLOCCO_GRADI = 2            # meno di BLOCCO_GRADI gradi, sta toccando qualcosa (arretra e riprova)
### [FIX 66] DOPO L'USCITA DALL'ARENA
ARENA_UNA_VOLTA = True      # True = dopo essere uscito dall'arena una striscia argento NON fa rientrare:
                            # vuol dire che il robot sta tornando indietro sulla linea, quindi fa dietrofront
FERMO_SOGLIA = 2.0          # [FIX 55] se in 1,5 s l'immagine della camera arena cambia meno di così (media dei
                            # pixel, 0-255) e il giroscopio non si muove, il robot è incastrato

### [FIX 54] SCARICO DELLE PALLINE NEL TRIANGOLO
# Prima il robot arrivava al triangolo e poi tornava indietro di 0,4 s prima di aprire la pinza: la pallina
# cadeva 3-8 cm PRIMA del bordo (simulatore). Ora si accosta piano finché il laser frontale legge SCARICO_CM
# (o finché non avanza più perché tocca il bordo) e lascia la pallina da lì.
SCARICO_CM = 3              # cm tra muso e bordo del triangolo al momento del rilascio
RETRO_SCARICO_S = 0.0       # s di retromarcia prima di aprire la pinza (prima 0.4). Alzatelo SOLO se il
                            # braccio, scendendo, tocca il bordo del triangolo
# [FIX 83] si scarica solo con il triangolo al centro dell'immagine della camera arena (224 pixel di larghezza)
SCARICO_CENTRO_PX = 40      # pixel dal centro (circa 12 gradi): oltre, prima mi giro verso il triangolo
SCARICO_ARRETRA_S = 0.5     # s di retromarcia prima di girarsi verso il triangolo (il muro è vicino)
# [FIX 84] prima di uscire dalla porta il robot si raddrizza e si centra sulla striscia NERA dell'uscita
USCITA_SQUADRA_GRADI = 3    # se la striscia è inclinata di più, prima ruoto (senza fidarmi del giroscopio)
USCITA_TOLLERANZA_CM = 3    # se il centro della porta è più lontano di così, prima mi sposto di lato
USCITA_FERMO_S = 1.2        # uscendo, se la striscia nera resta ferma nell'immagine per questi secondi...
USCITA_FERMO_PX = 4         # ...(entro questi pixel, immagine 440x260) il robot è contro lo stipite
DistanzaMuro = 10           # cm da tenere tra il fianco del robot e il muro
DistanzaAngolo = 15         # cm: laser frontale sotto questa distanza = angolo (o triangolo), giro di 90 gradi
PassiAperturaMax = 30       # passi da 0,1 s per entrare piano in un'apertura cercando la striscia
STRISCIA_AREA_MIN = 2500    # [FIX 39] pixel neri (immagine 224x224) per dire "striscia nera dell'uscita"

# [FIX 41] fine della svolta agli incroci
# [FIX 52] COME GIRA AGLI INCROCI CON IL VERDE
#   "vecchie" = come nel codice originale della squadra: avanti a tempo (0,45 s), poi Gira(42) a destra o
#               Gira(-35) a sinistra, e il seguilinea finisce la curva. Va meglio con gli incroci di forma
#               strana del vostro campo (richiesta del 22/10).
#   "nuove"   = FIX 41: avanza finché le ruote sono sopra l'incrocio, poi ruota finché vede la linea davanti
#               (SVOLTA_BASE, SVOLTA_MAX, DistanzaMusoRuote valgono solo con "nuove").
SVOLTE = "vecchie"
SVOLTA_BASE = 75            # gradi di svolta di base (prima 42 a destra e 35-37 a sinistra)
VERDE_PENDENZA_RISERVA_S = 1.5  # [FIX 124] svolta al verde in pendenza: se la linea trasversale non si misura (rotonda) avanza tanto (prima 0,5)
VERDE_PENDENZA_VEL_MIN = 22  # [FIX 121] velocità minima nella svolta al verde in pendenza (prima 14 in discesa: robot fermo; 22 = la velocità del seguilinea in discesa, che sul robot vero si muove)
VERDE_SALITA_AVANZA = True   # [FIX 118] interruttore: al verde in SALITA niente "1,3 s alla cieca", avanza sull'incrocio e poi gira (False = come la V50)
SWITCH_CONFERMA = True       # [FIX 117] interruttore: si passa all'arena solo se il robot è entrato; uno switch "spento" per un attimo non ferma il seguilinea
SWITCH_CONFERMA_S = 0.5      # [FIX 117] lo switch deve restare spento almeno così (motori fermi subito) per contare
SCATOLA_MIN_CAMPIONI_RUN = 20 # [FIX 122] il file dell'attesa si cancella se ha meno di tanti campioni con lo switch acceso (2 s)
IMPENNATA_RADDRIZZA = True    # [FIX 125] interruttore: robot sulle ruote davanti -> colpetti di retromarcia
IMPENNATA_GRADI = 35          # [FIX 125] beccheggio sotto -35 (la tavola dell'altalena arriva a circa -20; sul muso -60/-75)
IMPENNATA_LASER_CM = 10       # [FIX 125] ...e laser davanti sotto 10 cm (sul muso legge 4-6 cm: vede il pavimento)
IMPENNATA_CONFERMA_S = 0.4    # [FIX 125] nel seguilinea deve durare tanto (la caduta della tavola non conta)
IMPENNATA_VEL = 100           # [FIX 125] velocità del colpetto di retromarcia (massima)
IMPENNATA_COLPO_S = 0.2       # [FIX 125] durata del colpetto
IMPENNATA_ATTESA_S = 0.5      # [FIX 125] attesa prima di ricontrollare laser e giroscopio
IMPENNATA_TENTATIVI = 4       # [FIX 125] colpetti al massimo
LUCE_BECCHEGGIO_MAX = 15      # [FIX 126] con il robot inclinato più di così niente avviso della luce
ARRIVO_SULLA_ROSSA = True     # [FIX 127] interruttore: alla linea rossa ci va SOPRA, fermo ARRIVO_FERMO_S, poi la festa
ARRIVO_VEL = 30               # [FIX 127] velocità per salire sopra la linea rossa
ARRIVO_ROSSO_PIXEL = 40       # [FIX 127] sotto questi pixel rossi (immagine 112 x 112) la camera "non vede più" il rosso
ARRIVO_OLTRE_S = 0.6          # [FIX 127] dopo che il rosso è uscito dalla camera avanza ancora (simulatore: striscia a ~1 cm dal centro del robot)
ARRIVO_MAX_S = 4.0            # [FIX 127] al massimo avanza per tanto, poi si ferma comunque
ARRIVO_FERMO_S = 10.0         # [FIX 127] fermo sulla linea rossa prima della festa (il prof: 10 s; da controllare sul regolamento 2027)
LOP_TIENE_LA_GARA = True      # [FIX 128] dopo una LoP (switch spento meno di CRONO_NUOVA_GARA_S) arena e palline restano come erano
IMPENNATA_TOLLERANTE = True   # [FIX 129] laser a 0 col muso giù = vicino; col muso giù oltre IMPENNATA_SOLO_GIRO_GRADI basta il giroscopio
IMPENNATA_SOLO_GIRO_GRADI = 50  # [FIX 129]
ARENA_CONFERMA_PRESA = True   # [FIX 130] interruttore: carica la pallina solo se la seconda foto la vede vicina e del colore giusto
ARENA_CONFERMA_AREA = 3300    # [FIX 130] area minima (pixel su 224 x 224) nella seconda foto (il robot si ferma a 5500)
ARENA_NERA_V_MAX = 90         # [FIX 130] luminosità mediana del centro della pallina: fino a qui è NERA (19/11: nera 32-52)
ARENA_ARGENTO_V_MIN = 110     # [FIX 130] da qui in su è ARGENTO (19/11: argento 123-159); in mezzo decide YOLO
ARENA_LIBERA_DOPO_LOP = True  # [FIX 131] dopo una LoP dentro l'arena: ricerca LIBERA (argento e nere, ognuna nel suo triangolo)
ARENA_TEMPO_MAX = True        # [FIX 132] interruttore dei tempi massimi in arena
ARENA_CERCA_MAX_S = 60.0      # [FIX 132] senza portare palline per tanto: passa alla ricerca LIBERA
ARENA_LIBERA_MAX_S = 60.0     # [FIX 132] ricerca libera senza trovare niente per tanto: cerca l'uscita
LOP_RIFAI_ARENA = True        # [FIX 133] LoP dopo l'arena e robot rimesso prima dell'ingresso: rientra e rifà l'arena (ricerca libera)
LOP_RIFAI_ARENA_S = 60.0      # [FIX 133] per quanto, dopo la LoP, l'ingresso dell'arena vale di nuovo
CAM_ARENA_RITARA_IN_ARENA = True   # [FIX 134] all'inizio dell'arena la camera arena si ritara (automatica, poi blocco se ragionevole)
CAM_ARENA_RITARA_S = 1.2      # [FIX 134] secondi di esposizione automatica dentro l'arena prima del blocco
CAM_ARENA_ESPOSIZIONE_MAX_US = 20000  # [FIX 134] oltre: non si blocca (23/11: 48439 us = buio all'avvio; normale circa 10000)
CAM_ARENA_GAIN_MAX = 1.8      # [FIX 134] oltre: non si blocca (23/11: 2,0; normale 1,1-1,5)
ARENA_PAVIMENTO_BRUCIATO_V = 232  # [FIX 134] immagine arena con il pavimento così chiaro: il colore della pallina non vale
VERDE_SALITA_FINISCI = True   # [FIX 135] interruttore: verde visto in salita: prima finisce la salita, poi cerca l'incrocio
VERDE_SALITA_GRADI = 10       # [FIX 135] beccheggio sopra questo: è una salita
VERDE_SALITA_PIANO_GRADI = 8  # [FIX 135] beccheggio sotto questo per 0,2 s: salita finita
VERDE_SALITA_VEL = 34         # [FIX 135] velocità per finire la salita (quella del seguilinea in salita)
VERDE_SALITA_MAX_S = 4.0      # [FIX 135] al massimo
VERDE_SALITA_DOPO_S = 0.6     # [FIX 135] finita la salita, se la linea trasversale non si misura avanza tanto (circa 6 cm) e gira
VERDE_SALITA_DOPO_MAX_S = 1.0 # [FIX 135] finita la salita, comunque al massimo tanto (alla rotonda la misura sbaglia)
IMPENNATA_PROVA_AVANTI = True # [FIX 136] interruttore: dopo i colpetti indietro, colpetti IN AVANTI
IMPENNATA_INDIETRO_TENTATIVI = 2  # [FIX 136] colpetti di retromarcia prima di provare in avanti
IMPENNATA_AVANTI_S = 0.3      # [FIX 136] durata del colpetto in avanti
IMPENNATA_ANTERIORI = True    # [FIX 146] interruttore: sul muso prima SOLO LE RUOTE DAVANTI indietro al massimo (idea del prof, 26/11)
IMPENNATA_ANTERIORI_VEL = 100 # [FIX 146] velocità delle ruote davanti (massima)
IMPENNATA_ANTERIORI_S = 2.5   # [FIX 146] al massimo tanti secondi (si ferma appena il beccheggio torna sopra -IMPENNATA_GRADI)
IMPENNATA_ANTERIORI_TENTATIVI = 2  # [FIX 146] quante volte; poi i colpetti di prima (FIX 125 e 136)
ARENA_CONFERMA_DX = 50        # [FIX 137] la pallina della seconda foto deve essere a meno di tanti pixel (su 224) da quella della prima
ARENA_CONFERMA_DY = 45        # [FIX 137]
ARENA_DOPO_MANCATA_S = 40.0   # [FIX 137] dopo una presa mancata almeno tanti secondi per riprovare (max 3 volte)
FINE_SALITA_GUARDA = True     # [FIX 138] interruttore: verde in salita ricordato; a fine salita fermo e guardo
FINE_SALITA_INIZIO_GRADI = 12 # [FIX 138] beccheggio sopra questo: sto salendo
FINE_SALITA_PIANO_GRADI = 8   # [FIX 138] beccheggio sotto questo: di nuovo in piano (come VERDE_SALITA_PIANO_GRADI)
FINE_SALITA_MIN_S = 2.0       # [FIX 138] solo dopo una salita lunga almeno così
FINE_SALITA_PAUSA_S = 1.5     # [FIX 138] fermo a guardare
VERDE_SALITA_RICORDO_S = 10.0 # [FIX 138] per quanto vale il verde visto in salita
ARENA_RIENTRO_USCITA = True   # [FIX 139] LoP mentre cercava l'uscita: rientrato cerca subito l'uscita (niente palline)
PARETE_ANGOLO_STALLO = True   # [FIX 140] interruttore: muro davanti vicino ma non mi avvicino -> giro come in un angolo
PARETE_STALLO_CM = 35         # [FIX 140] laser davanti sotto questo...
PARETE_STALLO_S = 4.0         # [FIX 140] ...e in tanti secondi non scende di almeno 2 cm
OSCILLA_CONTROLLO = True      # [FIX 141] interruttore: destra-sinistra senza fine nel seguilinea
OSCILLA_FINESTRA_S = 6.0      # [FIX 141] secondi osservati
OSCILLA_CAMBI = 10            # [FIX 141] cambi di verso delle sterzate forti in quella finestra (12:25: circa 15 in 6 s)
OSCILLA_SPINTE = 3            # [FIX 141] ...e almeno tante "BOOOOOSter" (nell'angolo del quadrato una ogni secondo)
OSCILLA_GRADI = 40            # [FIX 141] ...con la rotta che non cambia più di così
OSCILLA_ERR = 140             # [FIX 141] errore da cui una sterzata è "forte": solo i valori al massimo (12:25: -145, +145, +169), quando il nero è ai lati e non in alto
OSCILLA_GIRA_GRADI = 30       # [FIX 141] per uscire: giro di tanto, poi finché la linea è davanti
OSCILLA_AVANTI_S = 0.5        # [FIX 141] poi avanzo tanto
OSCILLA_PAUSA_S = 8.0         # [FIX 141] dopo, per tanto non ricontrollo
OST_RAMPA_VERIFICA = True     # [FIX 142] interruttore: muso che si alza davanti a qualcosa: rampa solo se sale davvero
OST_RAMPA_VERIFICA_S = 1.5    # [FIX 142] secondi in cui continua per vedere se sale
OST_RAMPA_VEL = 34            # [FIX 142] a questa velocità (quella del seguilinea in salita)
OST_RAMPA_SICURA_GRADI = 14   # [FIX 142] beccheggio da cui è sicuramente una rampa (contro l'ostacolo: 8-11)
OST_DISTANZA_GIRO_CM = 12     # [FIX 142] confermato l'ostacolo arretra finché il laser davanti legge almeno tanto
FINE_SALITA_NO_ALTALENA = True  # [FIX 143] interruttore: se durante la sosta di fine salita la tavola si abbassa, niente sosta
FINE_SALITA_ALTALENA_GRADI = 10 # [FIX 143] beccheggio sotto -10 durante la sosta = altalena
CABINA_ALTO_CONTRASTO = True  # [FIX 144] cabina con etichette quasi bianche, cornice chiara e colori accesi (False = colori di prima)
LUCE_AVVISI = True            # [FIX 123] interruttore: avviso nella cabina e nella scatola nera se la luce è troppo alta o troppo bassa
LUCE_BIANCO_MIN = 120         # [FIX 123] pavimento nella camera linea (V, 75 percentile) sotto così = troppo scuro (gare buone 172-215)
LUCE_BIANCO_MAX = 232         # [FIX 123] ...sopra così = bruciato (16/11 mattina: 239-240)
LUCE_LUX_MIN = 500            # [FIX 123] lux della camera arena (ambiente) sotto così = troppo bassa (gare: 1400-14000), provvisorio
LUCE_LUX_MAX = 25000          # [FIX 123] ...sopra così = troppo alta, provvisorio
LUCE_CONFERMA_LETTURE = 2     # [FIX 123] il problema deve durare tante letture di fila (una al secondo)
LUCE_RIPETI_S = 15            # [FIX 123] finché dura, l'avviso si ripete ogni tanti secondi
PALLINA_BORDO_RIPROVA = True # [FIX 119] interruttore: pallina tagliata dal bordo dell'immagine -> mi giro e la riguardo prima di prenderla
PALLINA_BORDO_PX = 4         # [FIX 119] il riquadro tocca il bordo se arriva entro tanti pixel (immagine 224)
PALLINA_BORDO_EXTRA = 10     # [FIX 119] gradi in più verso la pallina (il pezzo che non si vede)
VERDE_DISCESA_AVANZA = True  # [FIX 115] interruttore: al verde in discesa niente retromarcia, avanza sull'incrocio e poi gira (False = come la V48)
SVOLTA_MAX = 115            # poi ruota piano finché la linea è davanti, ma mai oltre questi gradi in tutto
DistanzaMusoRuote = 11.5    # cm dal muso al centro delle ruote (MISURATA): il robot gira attorno a quel punto
# taratura della camera linea dalle foto del righello (8/10): servono per sapere a quanti cm è una linea
CAM_LINEA_ALTEZZA = 8.3     # cm da terra
CAM_LINEA_INCL = 75.3       # gradi sotto l'orizzontale (15 gradi dalla verticale)
CAM_LINEA_FY = 266.0        # pixel (immagine 440x260)
CAM_LINEA_OFFSET = -0.5     # cm: la camera è circa mezzo centimetro davanti al muso
SVOLTA_RIGHE_CENTRO = 0.6   # frazione delle righe basse dell'immagine con la linea al centro per dire "linea davanti"

# [FIX 36] secondo parere sui verdi: controlla con i colori che il verde sia PRIMA dell'incrocio
CONTROLLO_VERDE = True      # False = decide solo YOLO, come prima

### [FIX 45] SOGLIA DEL NERO (scala dei grigi)
# Un pixel è "nero" se la sua luminosità V (da 0 = nero a 255 = bianco) è <= SOGLIA_NERO.
# Prima era fissa a 80. Nelle vostre foto di calibrazione dell'8/10 il nastro nero va da V 25 a 105
# (è lucido e fa riflessi al centro dell'immagine) e il bianco da 155 a 198: con 80 si perdeva il
# 17-25% della linea. 110 sta a metà tra i due.
# La luce cambia da un campo all'altro: tarate con  python3 TaraNero.py  (scrive taratura_nero.json,
# che se esiste vale più di questo numero).
SOGLIA_NERO = 110
VERDE_NERO_RIGA = 80        # pixel neri in una riga (immagine 224x224) per dire "qui c'è la linea orizzontale"
VERDE_AREA_MIN = 250        # pixel: macchie verdi più piccole non contano
VERDE_Y_MIN = 45            # si giudica solo se l'incrocio è tra queste due righe dell'immagine:
VERDE_Y_MAX = 175           # più in basso il verde valido potrebbe essere già uscito dall'inquadratura
# [FIX 78] scatola nera 29/10: il robot, girando, ha rivisto lo stesso incrocio DI TRAVERSO e il controllo
# dei colori ha contato due verdi "prima della linea" -> dietrofront sbagliato.
VERDE_ANGOLO_MAX = 20       # gradi: se la linea dell'incrocio è più storta di così i colori non giudicano e decide
                            # YOLO da solo. Sono gradi nell'immagine 224x224, che è schiacciata (440x260 -> 224x224):
                            # 20 qui = circa 12 gradi veri. Con la piastrella della foto del 29/10 girata di 20 gradi
                            # la V26 diceva "Fr" (dietrofront), la V27 non giudica.
VERDE_LATO_MIN = 14         # pixel: una macchia verde più stretta di così è il bordo scuro del nastro, non un verde
VERDE_RIEMPIMENTO = 0.45    # la macchia deve riempire almeno questa parte del suo rettangolo (il quadratino sì,
                            # le frange lungo il nastro no)
# [FIX 79] DIETROFRONT SOLO SE SICURO: i colori devono dire "doppio verde" e da fermo deve riconfermarlo
DIETRO_CONFERMA = True
# [FIX 80] dopo una svolta al verde (destra o sinistra) lo stesso incrocio non si rivaluta. La pausa finisce
# quando la camera ha visto VERDE_PAUSA_FOTOGRAMMI fotogrammi di fila senza verde (l'incrocio è uscito
# dall'inquadratura), e comunque dopo VERDE_PAUSA_S secondi. Dopo un dietrofront niente pausa: nel campo
# contorto il robot torna subito all'incrocio di prima e lì deve girare.
# [FIX 91] 3.0 -> 1.0 s. Scatola nera 05/11 (V30), secondi 55-57: alla ROTONDA il robot entra girando a sinistra,
# 0,2 s dopo YOLO vede già il verde dell'uscita (Sx, sicurezza 0,85) ma per la pausa lo ignora per 1,5 s e
# all'uscita va dritto. Il verde dell'uscita resta sempre in vista, quindi la pausa non finiva mai prima dei 3 s.
# Stesso schema al secondo 7 (verde a destra ignorato per 1,3 s). Nel simulatore con 1,0 s: pista della scuola
# completa (ingresso, arena, uscita, linea rossa; prima non entrava mai) e nessun peggioramento sulle altre piste.
VERDE_PAUSA_S = 1.0
VERDE_PAUSA_FOTOGRAMMI = 4

# [FIX 81] INGRESSO DELL'ARENA SOLO IN PIANO. Scatola nera 29/10, secondo 93: all'inizio di una rampa (beccheggio
# 15) YOLO ha visto l'argento, il robot è "entrato" e ha avviato l'arena sulla rampa.
ARENA_PIANO_GRADI = 8       # beccheggio e rollio sotto questi gradi...
ARENA_PIANO_S = 1.0         # ...da almeno questi secondi
ARENA_IGNORA_S = 3.0        # dopo un falso argento, per questi secondi l'argento non si ricontrolla
ARGENTO_OGGETTO = True       # [FIX 147] interruttore: "argento" con un oggetto colorato vicino davanti = è l'ostacolo, non l'ingresso
ARGENTO_OGGETTO_CM = 25       # [FIX 147] ...se il laser davanti è sotto questi cm
ARGENTO_OGGETTO_FRAZ = 0.20   # [FIX 147] ...e più di questa parte del terzo alto dell'immagine è colorata (ingressi veri 0-10%,
                              # scatola di cartone 40-84%)
ARGENTO_OGGETTO_SAT = 60      # [FIX 147] "colorato" = saturazione sopra questo valore
ARGENTO_OGGETTO_IGNORA_S = 15.0  # [FIX 147] dopo, l'argento si ignora per tanti secondi (il tempo di aggirare l'ostacolo)
ARGENTO_FRONTE_MAX_CM = 150     # [FIX 111] all'ingresso il laser davanti deve vedere l'arena: oltre questi cm è pista (falso
                                #   argento: 12/11 160 cm). Ingressi veri della scuola: al massimo 105 cm (arena 90 cm di
                                #   fondo); l'arena del regolamento è profonda al massimo 120 cm. 0 = controllo spento.
                                #   Contano solo le letture vere: se il laser è "fuori portata" il controllo non blocca
ARGENTO_FRONTE_FINESTRA_S = 0.5 # [FIX 111] mediana del laser davanti su questi secondi
ARGENTO_DOPO_S = 0              # [FIX 111] niente ingresso nei primi N secondi della run (0 = spento: nelle prove vicino
                                #   all'arena l'ingresso vero arriva anche a 6 s). In gara, partendo lontano: es. 30

DIETROFRONT_PAUSA_S = 30    # [FIX 98] dopo l'arena: un solo dietrofront per un argento; se lo rivede entro tanti s lo ignora
INGRESSO_LIBERO_CM = 40     # [FIX 101] girato verso la porta, il laser davanti deve vedere almeno così (il fondo dell'arena);
                            # se vede meno è il muro accanto alla porta: il robot cerca l'apertura spostandosi di lato
ENTRATA_CERCA_PASSO_CM = 4.0    # [FIX 101] passo laterale della ricerca dell'apertura
ENTRATA_CERCA_PASSI = 5         # [FIX 101] passi per parte (prima dalla parte opposta all'ultima svolta)
ENTRATA_OLTRE_CM = 9.0          # [FIX 101] trovata l'apertura, ci si sposta ancora di tanto verso il centro della porta
USCITA_TENTATIVI = 5            # [FIX 103] tentativi per passare la porta d'uscita (poi si torna al giro dei muri)
USCITA_EXTRA_RITENTO_S = 0.6    # [FIX 103] uscita: dopo un ritento si avanza un po' di più (arretrando si perde strada)
USCITA_LIBERO_CM = 30           # [FIX 104] girato verso l'uscita, il laser davanti deve vedere almeno così (uscite vere del
                                # 5 e 6/11: 44-91 cm; il muro accanto alla porta: 13-14 cm); se no cerca l'apertura di lato
USCITA_NERO_PAUSA_S = 6.0       # [FIX 104] striscia nera davanti a un muro: per tanti secondi non la si considera più
ENTRATA_RITARDO_STERZO_S = 0.5  # [FIX 104] "girato da solo" vale solo se lo sterzo spinge nel verso giusto da almeno tanto
CERCA_SPAZIO_CM = 22            # [FIX 104] cercando l'apertura, prima arretra fino ad avere tanto spazio davanti (prima 16)
ALTALENA_ATTIVA = True          # [FIX 102] riconoscere l'altalena dal salto del beccheggio
ALTALENA_SALITA_MIN = 10        # [FIX 102] gradi di muso in su prima della caduta
ALTALENA_SALTO_GRADI = 30       # [FIX 102] di quanti gradi deve calare il beccheggio (05/11: da +21 a -49, cioè 70)
ALTALENA_FINESTRA_S = 1.2       # [FIX 102] ...entro quanti secondi
ALTALENA_STABILE_S = 0.5        # [FIX 102] giroscopio fermo per tanto (beccheggio < 8, rotta entro 3 gradi)
ALTALENA_ATTESA_MAX_S = 2.5     # [FIX 102] attesa massima del giroscopio
ALTALENA_AVANZA_S = 0.4         # [FIX 102] se la linea non si vede, avanza tanto e riguarda
ALTALENA_PAUSA_S = 4.0          # [FIX 102] dopo un'altalena, per tanto non se ne cerca un'altra

# [FIX 82] PENDENZA DAL GIROSCOPIO (si vede nel terminale, nella finestra di stato, nel cruscotto e nella
# scatola nera). Beccheggio > 0 = salita. Il rollio: inclinate il robot a mano verso DESTRA e guardate il
# cruscotto; se scrive "verso sinistra" mettete ROLLIO_POSITIVO_A_DESTRA = not ROLLIO_POSITIVO_A_DESTRA.
PENDENZA_INIZIO = 8         # gradi: oltre questi inizia un tratto inclinato
PENDENZA_FINE = 5           # gradi: sotto questi il tratto è finito (due soglie: niente sfarfallio)
PENDENZA_FINESTRA_S = 0.5   # si usa la mediana degli ultimi 0,5 s (i dossi e le scosse non contano)
PENDENZA_CONFERMA_S = 0.4   # il nuovo stato deve durare almeno così prima di essere annunciato
ROLLIO_POSITIVO_A_DESTRA = False

# [FIX 37] Terminale, scatola nera e cruscotto 3D (ViennaMonitor.py)
VERSIONE = "ClaudeRob V63"  # [FIX 151] Arduino staccato: riconnessione e motori fermi; [FIX 152] stato dell'Arduino in cabina; [FIX 149] salti della bussola tolti; [FIX 150] uscita in discesa riconosciuta; [FIX 147] la scatola dell'ostacolo non è l'ingresso; [FIX 148] ostacolo da tutti e due i lati (bordo della pista); [FIX 145] ostacolo e altalena superati nella cabina; [FIX 146] sul muso: solo ruote davanti indietro; [FIX 142] ostacolo che fa alzare il muso non è una rampa; [FIX 143] niente "fine salita" sull'altalena; [FIX 144] cabina più chiara
PANNELLO = False            # [FIX 42] finestra "ClaudeRob - STATO" con tutti i sensori e l'operazione in corso
                            # [FIX 109] dalla V44 spenta: la cabina del terminale (FIX 107) ha già tutto, camere comprese.
                            # True = si apre anche lei (per vedere le camere grandi)
FINESTRE_CAMERE = False     # [FIX 51] le due camere ora sono DENTRO la finestra di stato e non si bloccano più.
                            # True = si aprono ANCHE le vecchie finestre 'Linea' e 'Arena' di OpenCV
                            # (quelle si aggiornano solo quando il programma se ne ricorda)
RIGA_OGNI = 1.0             # [FIX 42] da Thonny: una riga con tutti i valori ogni quanti secondi
TERMINALE = "cabina"        # [FIX 107] "cabina" = CABINA DI PILOTAGGIO a riquadri (ViennaCabina.py): laser, assetto,
                            #   cronometro, le due camere in piccolo, motori, fasi della gara, eventi. Serve una finestra
                            #   di almeno 100 x 38 caratteri (in VNC ingranditela): se è più piccola si usa "pannello"
                            # "pannello" = eventi chiari in alto + pannello fisso in basso con tutti i valori
                            # "semplice" = solo eventi + una riga riassuntiva ogni 2 s (per Thonny)
                            # "tutto"    = stampa tutto come prima (lo fa anche DEBUG = True)
UN_SOLO_PROGRAMMA = True    # [FIX 110] un secondo programma del robot non parte se uno sta già girando
LUCCHETTO = "/tmp/clauderob_robot.lock"   # [FIX 110] il file del lucchetto (si libera da solo quando il programma finisce)
LUCCHETTO_ATTESA_S = 20     # [FIX 110] il secondo programma lascia il messaggio sullo schermo per tanti secondi, poi esce
CRONO_DURATA_S = 480.0      # [FIX 107] cronometro della cabina: 8 minuti di gara (dalla prima accensione dello switch)
CRONO_NUOVA_GARA_S = 120.0  # [FIX 107] switch spento più di così: la prossima accensione fa ripartire il cronometro da 0
                            #   (con spegnimenti più corti è una LoP: il cronometro va avanti e conta le LoP)
SCATOLA_NERA = True         # registra ogni run in CARTELLA_SCATOLA (permesso in gara: non comunica con niente)
CARTELLA_SCATOLA = "/home/pi/OneDrive/ScatolaNera/"
SCATOLA_FOTO = True         # nella scatola nera anche le miniature delle camere (2 al secondo)
CRUSCOTTO = True            # SOLO LABORATORIO: pagina web 3D su http://<ip-del-robot>:8000
                            # IN GARA: CRUSCOTTO = False e WiFi spento (regolamento RCJ Rescue 3.2.4)
PORTA_CRUSCOTTO = 8000
BATTERIA_INA219 = None      # indirizzo I2C dell'INA219 se lo montate (es. 0x45; NON 0x40/0x41: sono le PCA9685)
BATTERIA_CELLE = 3          # LiPo 3S = 11,1 V

# [FIX 113]- metadati e controllo vista (soglie provvisorie da tarare sul robot)
CAM_METADATI_INTERVALLO_S = 1.0
CAM_LUX_MIN = 10.0
CAM_LUX_MAX = 10000.0
CAM_NERO_MIN = 0.005
CAM_NERO_MAX = 0.65
CAM_AVVIO_ATTESA_S = 1.5
CAM_ARENA_AUTOESPOSIZIONE = True
CAM_ARENA_BLOCCA_ESPOSIZIONE = True
CAM_VISTA_ABILITATA = True

### [FIX 2/10] Interruttori per gara e debug
DEBUG = False               # True = stampa a ogni ciclo (utile in laboratorio, lento in gara)
### [FIX 31] Foto del percorso per riaddestrare la rete neurale (YOLO)
SALVA_FOTO = True           # True = salva le foto del percorso (le scrive un thread separato: il robot non rallenta)
CARTELLA_FOTO = "/home/pi/OneDrive/Incroci/"   # la stessa cartella usata prima per l'addestramento
FOTO_INTERVALLO = 0.5       # secondi minimi tra due foto della STESSA classe (Ln, Sx, Fr, PALLE...).
                            # Quando la classe cambia (es. da Ln a Sx) la foto si salva subito: sono le più utili.
FOTO_SPAZIO_MINIMO_MB = 1000   # se sulla SD restano meno di 1 GB liberi il salvataggio si ferma da solo

### [FIX 32] Festeggiamento all'arrivo sulla linea rossa
FESTA = True
FESTA_LAMPEGGI = 6          # quante volte i due LED si alternano all'inizio
FESTA_TEMPO_LED = 0.2       # secondi (i LED sono su relè: non scendere sotto 0,1 s)
FESTA_BRACCIO_BASSO = 100   # il braccio parte da qui...
FESTA_BRACCIO_ALTO = 40     # ...e si alza fino a qui (40 = braccio alzato, come in AlzaPinza)
FESTA_PINZA_APERTA = 160    # stessi valori di ApriPinza / ChiudiPinza
FESTA_PINZA_CHIUSA = 98
FESTA_PINZA_VOLTE = 3       # apri-chiudi della pinza

### [FIX 5] Taratura generica delle altre camere
# Per la camera linea V46 si usano i parametri dedicati qui sotto:
# l'esposizione viene bloccata dopo l'assestamento automatico con i LED accesi.
BLOCCA_ESPOSIZIONE = False

### [FIX 112] CAMERA LINEA: fuoco, frequenza e autotaratura all'avvio
# La camera è a circa 8,3 cm dal pavimento: 1/distanza = circa 12 diottrie.
# Picamera2 usa LensPosition in diottrie; il codice limita il valore al range
# realmente dichiarato dalla camera (alcuni moduli non arrivano a 8,3 cm).
# [FIX 114] INTERRUTTORE dell'autotaratura (feature flag): True = V46 (LED accesi, esposizione bloccata, soglia Otsu
# all'avvio del programma); False = come V45/V47 (esposizione automatica, soglia da taratura_nero.json o SOGLIA_NERO).
# Per tornare del tutto alla camera della V47: CAM_LINEA_AUTOTARATURA = False, CAM_LINEA_FUOCO_MANUALE = False, CAM_LINEA_FPS = 10.
CAM_LINEA_AUTOTARATURA = True
CAM_LINEA_CONTRASTO_MIN = 60        # [FIX 120] taratura buona solo se bianco - nero (canale V) è almeno così (16/11 mattina: 23)
CAM_LINEA_ESPOSIZIONE_MAX_US = 15000 # [FIX 120] ...e se l'esposizione non supera questi microsecondi (gare buone 7000, 16/11: 25343)
CAM_LINEA_RITARA_ALLO_SWITCH = True # [FIX 120] interruttore: se la taratura all'avvio è venuta male, la rifà quando si accende lo switch
CAM_LINEA_FUOCO_MANUALE = True
CAM_LINEA_FUOCO_CM = 8.3
CAM_LINEA_FPS = 20
# Prima si accendono i LED, si lascia assestare l'esposizione automatica,
# poi si blocca esposizione e guadagno prima di misurare la soglia Otsu.
CAM_LINEA_BLOCCA_ESPOSIZIONE = True
CAM_LINEA_ASSESTAMENTO_S = 1.5
CAM_LINEA_FOTOGRAMMI_OTSU = 7
CAM_LINEA_SOGLIA_MIN = 60
CAM_LINEA_SOGLIA_MAX = 170
CAM_LINEA_PIXEL_MIN_OTSU = 200

### [FIX 56] Ostacolo o rampa?
# Quando il laser frontale legge meno di 15 cm il robot avanza piano e decide:
OST_CONFERMA_CM = 8         # il laser scende fino a qui = ostacolo vero (una rampa da 20-25° non ci arriva mai)
OST_RAMPA_GRADI = 6         # il robot si inclina più di così = rampa (le ruote davanti stanno salendo)
OST_VEL_CONFERMA = 30       # velocità con cui avanza mentre controlla
OST_TEMPO_CONFERMA = 1.5    # secondi massimi di controllo (poi, per sicurezza, è un ostacolo)
### [FIX 87] Laser frontale filtrato (scatola nera 03/11: letture che saltano, ostacoli finti)
LASER_FR_FINESTRA_S = 0.3   # s: mediana delle letture del laser frontale in questo tempo
OST_FALSO_CM = 15           # finito il controllo, se la mediana del laser è da qui in su NON è un ostacolo
### [FIX 88] Bussola stimata quando il giroscopio è bloccato o l'Arduino tace (scatola nera 03/11)
BUSSOLA_STIMATA = True      # False = come prima (rotta 0 se il giroscopio non risponde)
GRADI_S_PER_VEL = 0.74      # gradi/s di rotazione sul posto per ogni punto di velocità (35 a vel 47, 50 a vel 68)
STIMA_CURVA = 0.5           # in curva (sterzo non ±100) la rotazione stimata è sterzo x GRADI_S_PER_VEL x questo
GIRO_BLOCCATO_GRADI = 60    # i motori girano il robot di tanti gradi e il giroscopio non cambia = bloccato
### [FIX 90] Ostacolo più furbo: pareti ai lati, niente spinte (scatola nera 03/11 V30)
OST_PARETE_CM = 18          # laser laterale sotto questa distanza = parete accanto al robot
OST_STACCO_GRADI = 20       # con una parete di lato: arretra e si gira di tanto verso la parte libera (poi 40, 60 se ci ricade)
OST_STACCO_RIPROVA_S = 8    # se entro questo tempo è di nuovo davanti a qualcosa, è un ostacolo vero
OST_LATO_LIBERO_CM = 30     # se a destra c'è meno spazio di così (e a sinistra di più) aggira a sinistra
OST_SPINTA_CM = 5           # laser frontale (filtrato) fino a qui mentre avanza = sta spingendo contro qualcosa
OST_SPINTA_ARRETRA_S = 0.5  # quanto arretra quando si accorge che spinge
ARDUINO_RICONNETTI = True   # [FIX 151] interruttore: errore di sistema ("Input/output error") o 3 errori in 2 s = Arduino staccato:
                            # dati a zero (motori fermi) e porta riaperta
ARDUINO_RICONNETTI_ATTESA_S = 1.0  # [FIX 151] attesa prima di riaprire la porta
BUSSOLA_TOGLI_SALTI = True  # [FIX 149] interruttore: i salti impossibili della rotta del BNO055 (26/11: +52 gradi in un pacchetto)
                            # si tolgono e la rotta continua da dove era
BUSSOLA_SALTO_GS = 200      # [FIX 149] il robot non gira più veloce di così (gradi al secondo; sul posto a 68 fa circa 50)
BUSSOLA_SALTO_TOLL = 15     # [FIX 149] gradi di tolleranza in più tra due pacchetti
USCITA_DISCESA_FUORI = True # [FIX 150] interruttore: uscendo dall'arena, muso giù (discesa) o laser davanti che si allunga = sono
                            # fuori, niente "non avanzo"
USCITA_DISCESA_GRADI = 8    # [FIX 150] beccheggio sotto -8 durante l'uscita = sto scendendo dalla porta
USCITA_LASER_APERTO_CM = 10 # [FIX 150] laser davanti più lungo di 10 cm rispetto a 0,6-0,9 s prima = non è uno stipite
OST_LATO_PREFERITO = "auto"  # [FIX 148] da che lato aggirare l'ostacolo: "auto" (i laser laterali, come prima), "destra" o
                             # "sinistra" (la squadra lo sceglie per la pista di oggi); se da quel lato non passa prova dall'altro
OST_BORDO = True             # [FIX 148] interruttore: sul primo lato, se la camera linea vede il BORDO DELLA PISTA torna indietro
                             # e aggira l'ostacolo dall'altro lato
OST_BORDO_BIANCO_MIN = 0.45  # [FIX 148] bordo = meno di così dell'immagine è pavimento bianco (seguilinea: quasi sempre oltre 0,6; bordo 05/11: 0,6 con 40% fuori)
OST_BORDO_V = 110            # [FIX 148] "bianco" = luminosità (V) sopra questo valore e poco colore
OST_BORDO_RICORDA_S = 120    # [FIX 148] per tanti secondi si ricorda il lato col bordo (dopo una LoP riparte dall'altro)
OST_ROTAZIONE_TOLL = 25     # rotazione dell'ostacolo rimasta a più di tanti gradi dall'obiettivo = bloccata

### [FIX 57] Interruzioni della linea
GAP_RETRO_S = 0.35          # s di retromarcia prima di allinearsi (la camera vede il pezzo dritto prima del vuoto)
GAP_TEMPO_MAX = 2.0         # s massimi di dritto col giroscopio sopra il vuoto (circa 25-30 cm)

GAP_SEGUI_FINO_AL_VUOTO = True   # [FIX 62] True = segue il nastro fino al vuoto e poi lo attraversa (AttraversaVuoto)
                                 # False = si ferma appena YOLO vede "Di" (AttraversaInterruzione, V23)
GAP_SEGUI_FILTRO_RIGHE = True   # [FIX 116] interruttore: alla fine del nastro ignora le righe sottili (fessure, scotch) e limita le rotazioni
GAP_RIGA_SOTTILE_PX = 15         # [FIX 116] righe nere più sottili di così (pixel su 440) non sono nastro (il nastro è circa 70 pixel)
GAP_SEGUI_MAX_GRADI = 45         # [FIX 116] mentre cerca la fine del nastro non ruota mai più di così in tutto
GAP_AVVICINA_S = 2.0        # [FIX 62] s massimi per seguire il nastro fino alla sua fine
GAP_NERO_MIN = 300          # [FIX 62] pixel neri sotto i quali il nastro è finito (il vuoto è sotto il muso)
GAP_CURVA_GRADI_S = 25      # [FIX 62] sopra questa velocità di rotazione il robot "sta curvando": vale il lato successivo nel verso della curva
GAP_CURVA_TOT_GRADI = 45    # [FIX 85] ...oppure se negli ultimi 2 s ha girato in tutto più di così (curva a U che rallenta)
GAP_SCATTO_GRADI = 42       # [FIX 62] entro questi gradi da un lato delle piastrelle attraversa il vuoto in quella direzione esatta (sotto 45: la direzione più vicina è quella giusta)

### [FIX 58] Linea persa: ricerca sicura (mai avanti alla cieca)
RECUPERO_SICURO = True      # False = vecchia ricerca (gira 25° e 50° e poi va avanti)
RECUPERO_ANGOLI = (-30, 30, -60, 60, -90, 90, -120, 120)   # gradi del ventaglio, rispetto a dove l'ha persa
                            # (fino a 120°: dopo un angolo acuto la linea riparte quasi all'indietro)
RECUPERO_RETRO_S = 1.0      # s massimi di retromarcia a piccoli passi sulla strada già fatta

### [FIX 59] Incroci senza verde: si attraversano dritti
INCROCI_DRITTI = True       # False = come prima (il PID segue il baricentro del nero)
INCROCIO_DRITTO_S = 0.7     # s di dritto col giroscopio per superare l'incrocio
INCROCIO_PAUSA_S = 2.0      # s dopo un incrocio in cui non se ne cerca un altro
INCROCIO_DOPO_SVOLTA_S = 2.0  # [FIX 92] dopo una svolta al verde, per tanti secondi niente "incrocio senza verde: dritto"

### [FIX 7] Contatori della gara
# True  = a ogni nuova accensione dello switch si azzerano palline salvate e posizioni.
# False = i contatori restano (utile se dopo un "lack of progress" in arena
#         il robot deve ricordarsi quante palline ha già portato).
AZZERA_CONTATORI_A_OGNI_AVVIO = True
