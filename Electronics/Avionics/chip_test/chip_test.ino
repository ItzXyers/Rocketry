/*
 * chip_test.ino  --  bench test for the flight-computer I2C sensors
 * -----------------------------------------------------------------------------
 * Sensors : BMP388 barometer (Qwiic)  +  ADXL375 +/-200 g accelerometer
 * Target  : any Arduino; primary target is a standard Uno / Nano (ATmega328, 5 V)
 *
 * For the Arduino Nano ESP32 (the flight computer), use the PlatformIO bench
 * env instead: firmware/  ->  pio run -e chips_bench -t upload
 * (src/bench_chips_main.cpp) -- it reuses the real flight sensor/logger/buzzer
 * modules and also covers the microSD reader, buzzer, and arm-interlock input.
 *
 * WHAT IT DOES
 *   setup() : scans the I2C bus, auto-detects each sensor's address (primary or
 *             jumper-swapped alternate), verifies each chip's identity register,
 *             then initialises both Adafruit drivers.
 *   loop()  : streams temperature / pressure / altitude and X/Y/Z acceleration,
 *             plus the acceleration vector magnitude (should read ~1 g at rest).
 *
 * SERIAL COMMANDS  (115200 baud)
 *   z   capture the current pressure as the altitude zero reference
 *   r   re-run the scan + identity diagnostics
 *   h   print the command list
 *
 * WIRING  (standard Arduino -- hardware I2C is fixed to A4/A5, not remappable)
 *   A4 -> SDA (blue)     A5 -> SCL (yellow)     3V3 -> V (red)     GND -> GND
 *   Daisy-chain the two boards by their second Qwiic port.
 *   Do NOT add pull-up resistors -- both breakouts already carry them.
 *
 *   !! VOLTAGE !!  The Adafruit ADXL375 is 5 V tolerant. The SparkFun-style
 *   BMP388 Qwiic board is 3.3 V ONLY (no level shifting). On a 5 V Arduino,
 *   power both boards from the 3V3 pin -- never 5 V -- or put a level shifter
 *   between the Arduino and the Qwiic chain, or run this on a 3.3 V board.
 *
 * LIBRARIES  (Arduino IDE -> Library Manager)
 *   "Adafruit BMP3XX Library"      "Adafruit ADXL375"
 *   Each pulls in Adafruit BusIO / Adafruit Unified Sensor / Adafruit ADXL343.
 * -----------------------------------------------------------------------------
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP3XX.h>
#include <Adafruit_ADXL375.h>

// ---- config --------------------------------------------------------------
static const uint32_t SERIAL_BAUD  = 115200;
static const uint16_t SAMPLE_MS    = 500;        // streaming interval
static float          seaLevel_hPa = 1013.25;   // 'z' updates this at runtime

// Candidate addresses: primary first, jumper-swapped alternate second.
static const uint8_t BMP_ADDRS[]  = { 0x77, 0x76 };
static const uint8_t ADXL_ADDRS[] = { 0x53, 0x1D };
static const uint8_t BMP_CHIP_ID  = 0x50;   // reg 0x00; a BMP390 would read 0x60
static const uint8_t ADXL_DEV_ID  = 0xE5;   // reg 0x00

// ---- globals --------------------------------------------------------------
Adafruit_BMP3XX  bmp;
Adafruit_ADXL375 accel = Adafruit_ADXL375(375);   // arg is an arbitrary sensor id

uint8_t  bmpAddr = 0, adxlAddr = 0;
bool     bmpOK = false, adxlOK = false;
uint32_t lastSample = 0;

// ---- low-level I2C helpers ---------------------------------------------
bool i2cPresent(uint8_t addr) {
  Wire.beginTransmission(addr);
  return Wire.endTransmission() == 0;
}

uint8_t readReg8(uint8_t addr, uint8_t reg) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission() != 0)            return 0xFF;
  if (Wire.requestFrom(addr, (uint8_t)1) != 1) return 0xFF;
  return Wire.read();
}

// ---- diagnostics -------------------------------------------------------
void scanBus() {
  Serial.println(F("I2C scan:"));
  uint8_t n = 0;
  for (uint8_t a = 1; a < 127; a++) {
    if (i2cPresent(a)) {
      Serial.print(F("  0x"));
      if (a < 16) Serial.print('0');
      Serial.println(a, HEX);
      n++;
    }
  }
  Serial.print(F("  "));
  Serial.print(n);
  Serial.println(F(" device(s)"));
}

// Walk the candidate addresses, return the one whose id register matches.
uint8_t findChip(const uint8_t *addrs, uint8_t count, uint8_t idReg,
                 uint8_t idWant, const __FlashStringHelper *name) {
  for (uint8_t i = 0; i < count; i++) {
    uint8_t a = addrs[i];
    if (!i2cPresent(a)) continue;
    uint8_t id = readReg8(a, idReg);
    Serial.print(F("  "));
    Serial.print(name);
    Serial.print(F(" at 0x"));
    Serial.print(a, HEX);
    Serial.print(F("  id=0x"));
    Serial.print(id, HEX);
    if (id == idWant) {
      Serial.println(F("  PASS"));
      return a;
    }
    Serial.print(F("  (want 0x"));
    Serial.print(idWant, HEX);
    Serial.println(F(")  mismatch"));
  }
  Serial.print(F("  "));
  Serial.print(name);
  Serial.println(F("  NOT FOUND"));
  return 0;
}

void runDiagnostics() {
  Serial.println(F("\n=== sensor diagnostics ==="));
  scanBus();

  bmpAddr  = findChip(BMP_ADDRS,  sizeof(BMP_ADDRS),  0x00, BMP_CHIP_ID, F("BMP388 "));
  adxlAddr = findChip(ADXL_ADDRS, sizeof(ADXL_ADDRS), 0x00, ADXL_DEV_ID, F("ADXL375"));

  bmpOK = adxlOK = false;

  if (bmpAddr && bmp.begin_I2C(bmpAddr)) {
    bmp.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
    bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
    bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
    bmp.setOutputDataRate(BMP3_ODR_50_HZ);
    bmpOK = true;
    Serial.println(F("  BMP388 driver init OK"));
  } else if (bmpAddr) {
    Serial.println(F("  BMP388 driver init FAILED"));
  }

  if (adxlAddr && accel.begin(adxlAddr)) {
    adxlOK = true;
    Serial.println(F("  ADXL375 driver init OK (+/-200 g)"));
  } else if (adxlAddr) {
    Serial.println(F("  ADXL375 driver init FAILED"));
  }

  Serial.println(F("=========================\n"));
}

void printHelp() {
  Serial.println(F("commands:  z = zero altitude   r = re-run diagnostics   h = help"));
}

// ---- Arduino entry points -------------------------------------------------
void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial && millis() < 3000) { }   // wait for USB serial, but don't hang

  Wire.begin();
  Wire.setClock(100000);   // 100 kHz for bring-up; both chips also do 400 kHz

  Serial.println(F("\nflight-computer sensor bench test"));
  runDiagnostics();
  printHelp();
}

void loop() {
  // --- serial commands ---
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'r') {
      runDiagnostics();
    } else if (c == 'h') {
      printHelp();
    } else if (c == 'z') {
      if (bmpOK && bmp.performReading()) {
        seaLevel_hPa = bmp.pressure / 100.0;
        Serial.print(F("zeroed: sea-level reference = "));
        Serial.print(seaLevel_hPa, 2);
        Serial.println(F(" hPa"));
      } else {
        Serial.println(F("zero failed: no BMP388 reading"));
      }
    }
  }

  // --- streaming ---
  if (millis() - lastSample < SAMPLE_MS) return;
  lastSample = millis();

  if (bmpOK) {
    if (bmp.performReading()) {
      Serial.print(F("BMP  T="));    Serial.print(bmp.temperature, 2);
      Serial.print(F(" C  P="));     Serial.print(bmp.pressure / 100.0, 2);
      Serial.print(F(" hPa  alt=")); Serial.print(bmp.readAltitude(seaLevel_hPa), 1);
      Serial.print(F(" m"));
    } else {
      Serial.print(F("BMP  read failed"));
    }
  } else {
    Serial.print(F("BMP  --"));
  }

  Serial.print(F("   |   "));

  if (adxlOK) {
    sensors_event_t e;
    accel.getEvent(&e);
    const float G = 9.80665;
    float x = e.acceleration.x / G;
    float y = e.acceleration.y / G;
    float z = e.acceleration.z / G;
    Serial.print(F("ACC  X="));      Serial.print(x, 2);
    Serial.print(F(" Y="));          Serial.print(y, 2);
    Serial.print(F(" Z="));          Serial.print(z, 2);
    Serial.print(F(" g   |mag|="));  Serial.print(sqrt(x * x + y * y + z * z), 2);
    Serial.println(F(" g"));
  } else {
    Serial.println(F("ACC  --"));
  }
}
