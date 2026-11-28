// =====================================================================================
//  InoSensorRobusto2.ino  -  Arduino Nano del robot gommato (RoboCup Junior Rescue Line)
//  IISS "Erodoto di Thurii" - 28/11/2026, partendo da InoSensorRobusto.ino (21/10)
//
//  COSA FA: legge 3 laser VL53L1X, il giroscopio BNO055 e i 2 switch e manda al Raspberry,
//  20 volte al secondo, una riga con 10 valori separati da virgole (230400 baud):
//
//     laser1,laser2,laser3,rotta,rollio,beccheggio,switch1,switch2,riavvii,urto_forte
//
//  STESSO FORMATO di prima (ViennaClsRobot.py vuole 10 valori): il Raspberry non va cambiato.
//
//  COSA C'E' DI NUOVO (segnato con [ARDUINO n]):
//   [ARDUINO 1] GIROSCOPIO BLOCCATO. Nelle scatole nere (16/11, 26/11 16:45) il giroscopio a
//               volte legge sempre (-2, -2, 0): e' il BNO055 che risponde tutti zeri (0,0,0 meno
//               le correzioni di -2). Lo sketch di prima lo credeva vivo e non lo riavviava mai.
//               Ora: 0,0,0 esatti per mezzo secondo = BNO055 bloccato -> si riavvia.
//   [ARDUINO 2] LASER FERMO. Se un laser non da' misure nuove per 1 secondo, si riavviano SOLO i
//               laser (circa 50 ms), al massimo una volta ogni 10 s: se un laser e' rotto davvero
//               il robot non resta senza dati (il BNO055 per ripartire ci mette quasi 1 s).
//   [ARDUINO 3] DIAGNOSI. Il 9o valore (prima "urto leggero", sempre 0: il Raspberry non lo usa)
//               ora dice quante volte i sensori sono ripartiti dall'accensione (0-999). Finisce
//               nella scatola nera (campo "tilt", primo numero). Il 10o resta com'era.
//   [ARDUINO 4] WATCHDOG: stesso interruttore di prima (USA_WATCHDOG), con le istruzioni per
//               capire se si puo' accendere.
//
//  Quello che c'era gia' (21/10) e resta: tempo massimo su I2C (25 ms) e sui laser, letture che
//  non aspettano, nessun ciclo infinito, sensori rimessi in piedi se l'I2C si blocca.
// =====================================================================================
#include <Wire.h>
#include <VL53L1X.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <avr/wdt.h>

// -------------------- IMPOSTAZIONI --------------------
// [ARDUINO 4] WATCHDOG: se la Nano resta bloccata per piu' di 1 secondo si riavvia da sola.
// Si puo' accendere (1) SOLO se la Nano ha il bootloader NUOVO. Come saperlo: nell'IDE di Arduino,
// Strumenti > Processore. Se il caricamento funziona con "ATmega328P" -> bootloader nuovo, si puo'
// mettere 1. Se funziona solo con "ATmega328P (Old Bootloader)" -> lasciare 0: con il bootloader
// vecchio il watchdog puo' far ripartire la Nano all'infinito (si sistema ricaricando con 0).
// Prova al banco: con 1, aprire il Monitor seriale a 230400 baud: devono arrivare le righe di
// numeri. Se si vede solo "READY" ripetuto o niente, ricaricare con 0.
#define USA_WATCHDOG 0

// Ultimo valore della riga: 1 = urto forte letto dal BNO055 (come InoSensorUrti.ino), 0 = sempre 0.
// ATTENZIONE: il Raspberry (RwdFoto.py, "tilt in azione") guarda questo valore: lasciare 0.
#define LEGGI_URTI 0

// -------------------- PIN (come InoSensorUrti.ino) --------------------
#define SW1_PIN 2
#define SW2_PIN 3
#define XSHUT_1 7
#define XSHUT_2 6
#define XSHUT_3 5

// -------------------- SENSORI --------------------
VL53L1X sensor1, sensor2, sensor3;
Adafruit_BNO055 bno = Adafruit_BNO055(55);
bool laserOk[3] = {false, false, false};
int  distanza[3] = {0, 0, 0};          // ultima distanza letta (cm): resta valida tra una misura e l'altra
unsigned long ultimaMisura[3] = {0, 0, 0};   // [ARDUINO 2] quando ogni laser ha dato l'ultima misura nuova
bool bnoOk = false;
unsigned long ultimoTentativoBno = 0;
unsigned long bnoZeriDa = 0;           // [ARDUINO 1] da quando il BNO055 legge 0,0,0 (0 = non legge zeri)

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 50;  // 20 Hz
unsigned int riavvii = 0;              // [ARDUINO 3] quante volte i sensori sono ripartiti (I2C, BNO, laser)

const unsigned long BNO_ZERI_MS = 500;      // [ARDUINO 1] 0,0,0 per mezzo secondo = bloccato
const unsigned long LASER_FERMO_MS = 1000;  // [ARDUINO 2] nessuna misura nuova per 1 s = laser fermo
const unsigned long LASER_RIAVVIO_OGNI_MS = 10000;  // [ARDUINO 2] al massimo un riavvio dei laser ogni 10 s
unsigned long ultimoRiavvioLaser = 0;

// -------------------- I2C con tempo massimo --------------------
void avviaI2C() {
  Wire.begin();
  Wire.setClock(100000);                    // 100 kHz: piu' lento ma molto piu' resistente ai disturbi
  Wire.setWireTimeout(25000, true);         // se una comunicazione dura piu' di 25 ms la interrompe e resetta il bus
}

// -------------------- LASER VL53L1X --------------------
bool avviaLaser(VL53L1X &s, uint8_t pin, uint8_t indirizzo) {
  digitalWrite(pin, HIGH);
  delay(10);
  s.setTimeout(100);                        // nessuna attesa infinita
  if (!s.init()) return false;
  s.setAddress(indirizzo);
  s.setDistanceMode(VL53L1X::Long);         // fino a ~4 m (come prima)
  s.setMeasurementTimingBudget(33000);      // misura da 33 ms...
  s.startContinuous(33);                    // ...ogni 33 ms
  return true;
}

void initVL53() {
  pinMode(XSHUT_1, OUTPUT);
  pinMode(XSHUT_2, OUTPUT);
  pinMode(XSHUT_3, OUTPUT);
  digitalWrite(XSHUT_1, LOW);               // tutti spenti: poi si accendono uno alla volta
  digitalWrite(XSHUT_2, LOW);               // e a ognuno si da' un indirizzo diverso
  digitalWrite(XSHUT_3, LOW);
  delay(10);
  laserOk[0] = avviaLaser(sensor1, XSHUT_1, 0x30);
  laserOk[1] = avviaLaser(sensor2, XSHUT_2, 0x31);
  laserOk[2] = avviaLaser(sensor3, XSHUT_3, 0x32);
  for (int i = 0; i < 3; i++) {
    ultimaMisura[i] = millis();             // [ARDUINO 2] si riparte a contare da adesso
    if (!laserOk[i]) { Serial.print("VL53L1X #"); Serial.print(i + 1); Serial.println(" FAIL"); }
  }
}

// Legge un laser SOLO se ha una misura nuova pronta: non aspetta mai
void leggiLaser(VL53L1X &s, int i) {
  if (!laserOk[i]) { distanza[i] = 0; return; }
  if (s.dataReady()) {
    distanza[i] = s.read(false) / 10;       // mm -> cm, come prima
    ultimaMisura[i] = millis();             // [ARDUINO 2]
  }
}

// -------------------- BNO055 --------------------
void initBNO() {
  bnoOk = bno.begin();                      // niente while(1): se non risponde si riprova dopo
  ultimoTentativoBno = millis();
  bnoZeriDa = 0;
  if (bnoOk) {
    delay(100);
    bno.setExtCrystalUse(true);
  } else {
    Serial.println("BNO055 FAIL");
  }
}

uint8_t readBNOInterrupt() {               // come InoSensorUrti.ino
  Wire.beginTransmission(0x28);
  Wire.write(0x37);                         // registro INT_STA
  if (Wire.endTransmission(false) != 0) return 0;
  if (Wire.requestFrom(0x28, 1) == 1) return Wire.read();
  return 0;
}

// -------------------- se l'I2C si blocca: si rimette tutto in piedi --------------------
void riavviaSensori() {
  if (riavvii < 999) riavvii++;             // [ARDUINO 3]
  Wire.clearWireTimeoutFlag();
  Wire.end();
  avviaI2C();
  initVL53();
  initBNO();
}

// -------------------- SETUP --------------------
void setup() {
  MCUSR = 0;
  wdt_disable();                            // se ci si e' riavviati per il watchdog, lo si spegne subito
  Serial.begin(230400);
  avviaI2C();
  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  initVL53();
  initBNO();
  Serial.println("READY");
#if USA_WATCHDOG
  wdt_enable(WDTO_1S);
#endif
}

// -------------------- LOOP --------------------
void loop() {
#if USA_WATCHDOG
  wdt_reset();                              // "sono vivo": se non arriva per 1 s la Nano si riavvia
#endif

  if (Wire.getWireTimeoutFlag()) {          // una comunicazione I2C si era inchiodata
    riavviaSensori();
  }
  if (!bnoOk && millis() - ultimoTentativoBno > 2000) {
    initBNO();                              // il giroscopio non c'era: si riprova ogni 2 s
  }

  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();

    leggiLaser(sensor1, 0);
    leggiLaser(sensor2, 1);
    leggiLaser(sensor3, 2);
    // [ARDUINO 2] un laser acceso che non da' misure nuove da 1 s: si riavviano solo i laser
    for (int i = 0; i < 3; i++) {
      if (laserOk[i] && millis() - ultimaMisura[i] > LASER_FERMO_MS
          && millis() - ultimoRiavvioLaser > LASER_RIAVVIO_OGNI_MS) {
        Serial.print("LASER #"); Serial.print(i + 1); Serial.println(" FERMO: riavvio i laser");
        ultimoRiavvioLaser = millis();
        if (riavvii < 999) riavvii++;       // [ARDUINO 3]
        initVL53();
        break;
      }
    }

    int heading = 0, roll = 0, pitch = 0;
    if (bnoOk) {
      sensors_event_t orientation;
      bno.getEvent(&orientation, Adafruit_BNO055::VECTOR_EULER);
      // [ARDUINO 1] tutti e tre ESATTAMENTE 0 (un giroscopio vero ha sempre qualche decimale):
      // per mezzo secondo di fila = BNO055 bloccato -> si riavvia (al giro dopo si riprova)
      if (orientation.orientation.x == 0.0 && orientation.orientation.y == 0.0 && orientation.orientation.z == 0.0) {
        if (bnoZeriDa == 0) bnoZeriDa = millis();
        else if (millis() - bnoZeriDa > BNO_ZERI_MS) {
          Serial.println("BNO055 BLOCCATO (0,0,0): lo riavvio");
          if (riavvii < 999) riavvii++;     // [ARDUINO 3]
          initBNO();
        }
      } else {
        bnoZeriDa = 0;
      }
      heading = int(orientation.orientation.x);
      roll    = int(orientation.orientation.z - 2);   // stesse correzioni di InoSensorUrti.ino
      pitch   = int(orientation.orientation.y - 2);
    }

    int sw1 = (digitalRead(SW1_PIN) == LOW) ? 1 : 0;  // stessa codifica di prima
    int sw2 = (digitalRead(SW2_PIN) == LOW) ? 1 : 0;

    int urtoForte = 0;
#if LEGGI_URTI
    uint8_t ist = readBNOInterrupt();
    urtoForte = (ist & (1 << 4)) ? 1 : 0;
#endif

    Serial.print(distanza[0]); Serial.print(",");
    Serial.print(distanza[1]); Serial.print(",");
    Serial.print(distanza[2]); Serial.print(",");
    Serial.print(heading);     Serial.print(",");
    Serial.print(roll);        Serial.print(",");
    Serial.print(pitch);       Serial.print(",");
    Serial.print(sw1);         Serial.print(",");
    Serial.print(sw2);         Serial.print(",");
    Serial.print(riavvii);     Serial.print(",");   // [ARDUINO 3] prima "urto leggero" (sempre 0)
    Serial.println(urtoForte);
  }
}
