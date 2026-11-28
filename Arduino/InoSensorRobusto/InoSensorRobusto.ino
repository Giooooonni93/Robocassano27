// =====================================================================================
//  InoSensorRobusto.ino  -  Arduino Nano del robot gommato (RoboCup Junior Rescue Line)
//  IISS "Erodoto di Thurii" - versione scritta il 21/10/2026 partendo da InoSensorUrti.ino
//
//  COSA FA: legge 3 laser VL53L1X, il giroscopio BNO055 e i 2 switch e manda al Raspberry,
//  20 volte al secondo, una riga con 10 valori separati da virgole (230400 baud):
//
//     laser1,laser2,laser3,rotta,rollio,beccheggio,switch1,switch2,urto_leggero,urto_forte
//
//  E' lo stesso formato dello sketch che c'era prima (ViennaClsRobot.py vuole 10 valori).
//  Pin, ordine dei laser, correzioni del giroscopio e codifica degli switch sono gli stessi
//  di InoSensorUrti.ino. Gli ultimi due valori (sul Raspberry si chiamano "tilt") oggi il
//  programma del robot non li usa.
//
//  PERCHE' UNA VERSIONE NUOVA: il 21/10 alle 10:52 (scatola nera, secondo 442.9) l'Arduino
//  si e' bloccato e non ha piu' mandato dati: il robot e' rimasto senza laser e senza bussola.
//  Negli sketch vecchi ci sono tre punti dove la Nano puo' fermarsi PER SEMPRE:
//    1) la comunicazione I2C (Wire) non ha un tempo massimo: un disturbo dei motori la inchioda;
//    2) sensor.read() aspetta la misura nuova senza tempo massimo;
//    3) se il BNO055 non risponde all'accensione c'e' un while(1) infinito.
//  Qui ci sono: tempo massimo su I2C e sui laser, letture che non aspettano, nessun ciclo
//  infinito, reinizializzazione dei sensori se l'I2C si blocca e (se attivo) il watchdog.
// =====================================================================================
#include <Wire.h>
#include <VL53L1X.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <avr/wdt.h>

// -------------------- IMPOSTAZIONI --------------------
// WATCHDOG: se la Nano resta bloccata per piu' di 1 secondo si riavvia da sola.
// ATTENZIONE: le Nano con il BOOTLOADER VECCHIO (quelle che si caricano con
// "ATmega328P (Old Bootloader)", 57600 baud) con il watchdog possono restare in un ciclo di
// riavvii. Mettete 1 SOLO se caricate con "ATmega328P" normale (bootloader nuovo, 115200).
#define USA_WATCHDOG 0

// Ultimi due valori della riga: 1 = legge gli urti dal BNO055 come InoSensorUrti.ino,
// 0 = manda sempre 0,0 (meno traffico sull'I2C; il Raspberry oggi non li usa).
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
bool bnoOk = false;
unsigned long ultimoTentativoBno = 0;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 50;  // 20 Hz
unsigned int blocchiI2C = 0;                // quante volte l'I2C si e' bloccato (solo per diagnosi)

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
  s.startContinuous(33);                    // ...ogni 33 ms (prima 30 ms con misura da 50: troppo stretto)
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
    if (!laserOk[i]) { Serial.print("VL53L1X #"); Serial.print(i + 1); Serial.println(" FAIL"); }
  }
}

// Legge un laser SOLO se ha una misura nuova pronta: non aspetta mai
void leggiLaser(VL53L1X &s, int i) {
  if (!laserOk[i]) { distanza[i] = 0; return; }
  if (s.dataReady()) {
    distanza[i] = s.read(false) / 10;       // mm -> cm, come prima
  }
}

// -------------------- BNO055 --------------------
void initBNO() {
  bnoOk = bno.begin();                      // niente while(1): se non risponde si riprova dopo
  ultimoTentativoBno = millis();
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
  blocchiI2C++;
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

    int heading = 0, roll = 0, pitch = 0;
    if (bnoOk) {
      sensors_event_t orientation;
      bno.getEvent(&orientation, Adafruit_BNO055::VECTOR_EULER);
      heading = int(orientation.orientation.x);
      roll    = int(orientation.orientation.z - 2);   // stesse correzioni di InoSensorUrti.ino
      pitch   = int(orientation.orientation.y - 2);
    }

    int sw1 = (digitalRead(SW1_PIN) == LOW) ? 1 : 0;  // stessa codifica di prima
    int sw2 = (digitalRead(SW2_PIN) == LOW) ? 1 : 0;

    int urtoLeggero = 0, urtoForte = 0;
#if LEGGI_URTI
    uint8_t ist = readBNOInterrupt();
    urtoLeggero = (ist & (1 << 5)) ? 1 : 0;
    urtoForte   = (ist & (1 << 4)) ? 1 : 0;
#endif

    Serial.print(distanza[0]); Serial.print(",");
    Serial.print(distanza[1]); Serial.print(",");
    Serial.print(distanza[2]); Serial.print(",");
    Serial.print(heading);     Serial.print(",");
    Serial.print(roll);        Serial.print(",");
    Serial.print(pitch);       Serial.print(",");
    Serial.print(sw1);         Serial.print(",");
    Serial.print(sw2);         Serial.print(",");
    Serial.print(urtoLeggero); Serial.print(",");
    Serial.println(urtoForte);
  }
}
