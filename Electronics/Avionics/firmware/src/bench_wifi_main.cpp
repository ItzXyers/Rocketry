// Standalone WiFi bench — the chips_bench console (bench_chips_main.cpp),
// reachable over the flight computer's own WiFi AP instead of only USB.
// For bench work with the board on battery / inside the sled, where a USB
// cable isn't practical.
//
// Brings up the same AP the flight firmware uses (WIFI_AP_SSID /
// WIFI_AP_PASSWORD from config.h, 192.168.4.1), after the sensors and flash
// are up — same ordering as main.cpp. Join it from a laptop/phone, then:
//
//   http://192.168.4.1/              browser console (command box + live readout)
//   GET  /sample                     one fused sensor sample + battery, JSON
//   GET  /cmd?c=<command>            run one console command, plain-text reply
//   GET  /log?n=<nnn>                download FLIGHTnnn.CSV
//
// e.g.  curl "http://192.168.4.1/cmd?c=SCAN"
//
// Commands are the chips_bench set (SCAN ID INIT SELFTEST READ PEEK POKE
// FLASH LOGS FORMAT BUZZER BATT PINS HELP); STREAM is serial-only — the
// browser page polls /sample instead. The USB serial console still works in
// parallel and takes the same commands.
//
// The AP never latches off (there is no flight state machine), so this
// binary must not fly.
//
// Build/flash/monitor:
//   pio run -e wifi_bench -t upload
//   pio device monitor          (115200 baud)
//
// Re-flash the flight firmware (pio run -e nano_esp32 -t upload) and
// power-cycle before flying.

#include "battery.h"
#include "buzzer.h"
#include "config.h"

#include "logger.h"
#include "sensors.h"

#include <Arduino.h>
#include <StreamString.h>
#include <WebServer.h>
#include <WiFi.h>
#include <Wire.h>

namespace {

constexpr uint32_t BENCH_STREAM_INTERVAL_MS = 200; // ~5 Hz, readable on a console

WebServer g_server(WIFI_AP_HTTP_PORT);

bool g_sensorsUp = false;
bool g_streaming = false; // serial only
uint32_t g_lastStreamAt = 0;

// --- small output helpers -------------------------------------------------

void printHex8(Print &out, uint8_t v) {
  out.print(F("0x"));
  if (v < 0x10) out.print('0');
  out.print(v, HEX);
}

// --- raw I2C, no driver object ------------------------------------------

bool i2cPing(uint8_t addr) {
  Wire.beginTransmission(addr);
  return Wire.endTransmission() == 0;
}

// Returns the register value 0..255, or -1 if the device did not respond.
int i2cReadReg(uint8_t addr, uint8_t reg) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission() != 0) return -1;
  if (Wire.requestFrom(static_cast<uint8_t>(addr), static_cast<uint8_t>(1)) != 1) return -1;
  return Wire.read();
}

bool i2cWriteReg(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

// --- command implementations (all write to `out`: Serial or an HTTP body) --

void cmdScan(Print &out) {
  out.println(F("[bench] I2C scan:"));
  uint8_t n = 0;
  for (uint8_t a = 1; a < 127; a++) {
    if (i2cPing(a)) {
      out.print(F("[bench]   "));
      printHex8(out, a);
      out.println();
      n++;
    }
  }
  out.print(F("[bench] "));
  out.print(n);
  out.println(F(" device(s)"));
}

void probeChip(Print &out, const __FlashStringHelper *name, const uint8_t *addrs, uint8_t count,
               uint8_t idReg, uint8_t idWant) {
  bool any = false;
  for (uint8_t i = 0; i < count; i++) {
    if (!i2cPing(addrs[i])) continue;
    any = true;
    int v = i2cReadReg(addrs[i], idReg);
    out.print(F("[bench] "));
    out.print(name);
    out.print(F(" at "));
    printHex8(out, addrs[i]);
    out.print(F("  id="));
    if (v < 0) {
      out.println(F("(no response)"));
      continue;
    }
    printHex8(out, static_cast<uint8_t>(v));
    out.print(F("  want "));
    printHex8(out, idWant);
    out.println(v == idWant ? F("  MATCH") : F("  mismatch"));
  }
  if (!any) {
    out.print(F("[bench] "));
    out.print(name);
    out.println(F("  not present at either address"));
  }
}

void cmdId(Print &out) {
  static const uint8_t bmpAddrs[] = {0x76, 0x77};
  static const uint8_t adxlAddrs[] = {0x53, 0x1D};
  probeChip(out, F("BMP388 "), bmpAddrs, 2, 0x00, 0x50);  // CHIP_ID; BMP390 would be 0x60
  probeChip(out, F("ADXL375"), adxlAddrs, 2, 0x00, 0xE5); // DEVID
}

void printSample(Print &out, const SensorSample &s) {
  out.print(F("[bench] t="));
  out.print(s.timestamp_ms);
  out.print(F("ms  baro(v="));
  out.print(s.baro_valid ? 1 : 0);
  out.print(F(") P="));
  out.print(s.pressure_pa, 1);
  out.print(F("Pa T="));
  out.print(s.temperature_c, 2);
  out.print(F("C alt="));
  out.print(s.altitude_agl_m, 2);
  out.print(F("m   accel(v="));
  out.print(s.accel_valid ? 1 : 0);
  out.print(F(") g=("));
  out.print(s.accel_x_g, 3);
  out.print(F(", "));
  out.print(s.accel_y_g, 3);
  out.print(F(", "));
  out.print(s.accel_z_g, 3);
  out.print(F(")  |mag|="));
  out.print(s.accel_mag_g, 3);
  out.println(F("g"));
}

void cmdInit(Print &out) {
  g_sensorsUp = sensors_init();
  // The first BMP388 performReading() after init returns stale power-on
  // registers (bench, 2026-10-19: 77.9 kPa vs ~103.6 kPa) -- discard it so the
  // first /sample isn't garbage. Flight gets the same effect via selfTest().
  if (g_sensorsUp) sensors_read();
  out.print(F("[bench] sensors_init() = "));
  out.println(g_sensorsUp ? F("OK (both chips up)") : F("FAIL (see SELFTEST / SCAN / ID)"));
}

void cmdFlash(Print &out) {
  bool ok = logger_init(); // its own [logger] lines go to USB serial only
  out.print(F("[bench] logger_init "));
  out.println(ok ? F("OK") : F("FAIL (details on USB serial)"));
  if (!ok) return;
  LogRecord r;
  r.timestamp_ms = millis();
  logger_logEvent("benchtest", r);
  out.print(F("[bench] wrote one 'benchtest' record to FLIGHT"));
  uint16_t n = logger_currentFileNumber();
  if (n < 100) out.print('0');
  if (n < 10) out.print('0');
  out.print(n);
  out.print(F(".CSV, flush took "));
  out.print(logger_maxFlushUs());
  out.println(F(" us. Run FLASH once per boot — each call opens another file."));
}

void cmdBuzzer(Print &out, const String &arg) {
  // buzzer_setPattern() ignores a repeat of the current pattern, and a
  // finished one-shot (PASS, also played at boot) still counts as current --
  // so reset to OFF first, or a second BUZZER PASS would stay silent.
  buzzer_setPattern(BuzzerPattern::OFF);
  if (arg == "PASS") {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_PASS);
    out.println(F("[bench] buzzer: SELF_TEST_PASS (short double-beep, once)"));
  } else if (arg == "FAIL") {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_FAIL);
    out.println(F("[bench] buzzer: SELF_TEST_FAIL (fast continuous)"));
  } else if (arg == "BEACON") {
    buzzer_setPattern(BuzzerPattern::RECOVERY_BEACON);
    out.println(F("[bench] buzzer: RECOVERY_BEACON (slow chirp)"));
  } else if (arg == "OFF") {
    buzzer_setPattern(BuzzerPattern::OFF);
    out.println(F("[bench] buzzer: OFF"));
  } else {
    out.println(F("[bench] usage: BUZZER PASS|FAIL|BEACON|OFF"));
  }
}

void cmdBatt(Print &out) {
  uint32_t pinMv = analogReadMilliVolts(PIN_BATT_SENSE);
  out.print(F("[bench] BATT sense (" PIN_BATT_SENSE_NAME ") pin = "));
  out.print(pinMv);
  out.print(F(" mV  -> cell = "));
  out.print(battery_voltage(), 3);
  out.print(F(" V filtered, ~"));
  out.print(battery_percent());
  out.print(F(" %"));
  if (!battery_valid()) out.print(F("  (NO READING: divider fitted? on battery, not USB-only?)"));
  else if (battery_low()) out.print(F("  LOW"));
  out.println();
}

void cmdPins(Print &out) {
  out.println(F("[bench] pin map (Arduino label = ESP32-S3 GPIO):"));
  out.print(F("[bench]   I2C   SDA=A4("));   out.print(PIN_I2C_SDA);
  out.print(F(")  SCL=A5("));                out.print(PIN_I2C_SCL);   out.println(')');
  out.print(F("[bench]   BUZZER=D9("));      out.print(PIN_BUZZER);     out.println(')');
  out.print(F("[bench]   BATT_SENSE=" PIN_BATT_SENSE_NAME "("));  out.print(PIN_BATT_SENSE); out.println(')');

  out.print(F("[bench]   BMP388 addr (flight, pinned) = "));
  printHex8(out, BMP388_I2C_ADDR);
  out.println();
}

void cmdWifi(Print &out) {
  out.print(F("[bench] AP \""));
  out.print(WIFI_AP_SSID);
  out.print(F("\" ip "));
  out.print(WiFi.softAPIP());
  out.print(F("  ch "));
  out.print(WIFI_AP_CHANNEL);
  out.print(F("  clients "));
  out.println(WiFi.softAPgetStationNum());
}

void cmdHelp(Print &out) {
  out.println(F("[bench] commands:"));
  out.println(F("[bench]   SCAN                        I2C bus scan"));
  out.println(F("[bench]   ID                          BMP388/ADXL375 identity-register probe"));
  out.println(F("[bench]   INIT                        sensors_init()  (run automatically at boot)"));
  out.println(F("[bench]   SELFTEST                    sensors_selfTest()"));
  out.println(F("[bench]   READ                        one fused sensor sample"));
  out.println(F("[bench]   STREAM                      toggle ~5 Hz sampling (USB serial only)"));
  out.println(F("[bench]   PEEK <addr> <reg>           raw I2C read  (hex, e.g. PEEK 76 00)"));
  out.println(F("[bench]   POKE <addr> <reg> <val>     raw I2C write (hex) — no guard rails"));
  out.println(F("[bench]   FLASH                       mount internal flash + write a test record"));
  out.println(F("[bench]   LOGS                        list flight logs in internal flash"));
  out.println(F("[bench]   FORMAT YES                  erase every log (formats a new board)"));
  out.println(F("[bench]   BUZZER PASS|FAIL|BEACON|OFF  play a buzzer pattern"));
  out.println(F("[bench]   BATT                        battery voltage (" PIN_BATT_SENSE_NAME " divider)"));
  out.println(F("[bench]   PINS                        print the pin map"));
  out.println(F("[bench]   WIFI                        AP name / IP / connected clients"));

}

// --- command dispatch -------------------------------------------------

uint8_t tokenize(const String &line, String *out, uint8_t maxTokens) {
  uint8_t n = 0;
  int i = 0;
  const int len = line.length();
  while (i < len && n < maxTokens) {
    while (i < len && line[i] == ' ') i++;
    if (i >= len) break;
    int start = i;
    while (i < len && line[i] != ' ') i++;
    out[n++] = line.substring(start, i);
  }
  return n;
}

// `fromSerial` gates STREAM, which only makes sense on a live console.
void handleCommand(String line, Print &out, bool fromSerial) {
  line.trim();
  line.toUpperCase();
  if (line.length() == 0) return;

  String tok[4];
  uint8_t ntok = tokenize(line, tok, 4);
  const String &cmd = tok[0];

  if (cmd == "SCAN") {
    cmdScan(out);
  } else if (cmd == "ID") {
    cmdId(out);
  } else if (cmd == "INIT") {
    cmdInit(out);
  } else if (cmd == "SELFTEST") {
    bool ok = sensors_selfTest(); // per-chip [selftest] lines go to USB serial only
    out.print(F("[bench] sensors_selfTest() = "));
    out.println(ok ? F("PASS") : F("FAIL"));
  } else if (cmd == "READ") {
    printSample(out, sensors_read());
  } else if (cmd == "STREAM") {
    if (!fromSerial) {
      out.println(F("[bench] STREAM is USB-serial only — the web page polls /sample instead"));
    } else {
      g_streaming = !g_streaming;
      out.println(g_streaming ? F("[bench] streaming ON — send STREAM again to stop")
                              : F("[bench] streaming OFF"));
    }
  } else if (cmd == "PEEK") {
    if (ntok < 3) {
      out.println(F("[bench] usage: PEEK <addr_hex> <reg_hex>"));
    } else {
      uint8_t addr = strtol(tok[1].c_str(), nullptr, 16);
      uint8_t reg = strtol(tok[2].c_str(), nullptr, 16);
      int v = i2cReadReg(addr, reg);
      out.print(F("[bench] PEEK "));
      printHex8(out, addr);
      out.print(F(" reg "));
      printHex8(out, reg);
      out.print(F(" = "));
      if (v < 0) {
        out.println(F("(no response)"));
      } else {
        printHex8(out, static_cast<uint8_t>(v));
        out.print(F("  0b"));
        for (int b = 7; b >= 0; b--) out.print((v >> b) & 1);
        out.println();
      }
    }
  } else if (cmd == "POKE") {
    if (ntok < 4) {
      out.println(F("[bench] usage: POKE <addr_hex> <reg_hex> <val_hex>"));
    } else {
      uint8_t addr = strtol(tok[1].c_str(), nullptr, 16);
      uint8_t reg = strtol(tok[2].c_str(), nullptr, 16);
      uint8_t val = strtol(tok[3].c_str(), nullptr, 16);
      bool ok = i2cWriteReg(addr, reg, val);
      out.print(F("[bench] POKE "));
      printHex8(out, addr);
      out.print(F(" reg "));
      printHex8(out, reg);
      out.print(F(" <- "));
      printHex8(out, val);
      out.println(ok ? F("  ack") : F("  no ack"));
    }
  } else if (cmd == "FLASH") {
    cmdFlash(out);
  } else if (cmd == "LOGS") {
    logger_list(out);
  } else if (cmd == "FORMAT") {
    if (ntok >= 2 && tok[1] == "YES") {
      bool ok = logger_format();
      out.println(ok ? F("[bench] format OK") : F("[bench] format FAILED"));
    } else {
      out.println(F("[bench] FORMAT erases EVERY flight log. Send 'FORMAT YES' to confirm."));
    }
  } else if (cmd == "BUZZER") {
    cmdBuzzer(out, ntok >= 2 ? tok[1] : String());
  } else if (cmd == "BATT") {
    cmdBatt(out);
  } else if (cmd == "PINS") {
    cmdPins(out);
  } else if (cmd == "WIFI") {
    cmdWifi(out);
  } else if (cmd == "HELP" || cmd == "?") {
    cmdHelp(out);
  } else {
    out.print(F("[bench] unknown command: "));
    out.println(cmd);
    out.println(F("[bench] type HELP"));
  }
}

void pollSerialCommands() {
  static String buf;
  while (Serial.available() > 0) {
    char c = static_cast<char>(Serial.read());
    if (c == '\n' || c == '\r') {
      if (buf.length() > 0) {
        handleCommand(buf, Serial, /*fromSerial=*/true);
        buf = "";
      }
    } else {
      buf += c;
    }
  }
}

// --- HTTP -------------------------------------------------------------

const char INDEX_HTML[] PROGMEM = R"HTML(<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FC WiFi bench</title>
<style>
body{font:14px system-ui,sans-serif;margin:0;padding:12px;background:#111;color:#ddd}
h1{font-size:16px;margin:0 0 8px}
#live{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px;margin-bottom:10px}
#live div{background:#1d1d1d;padding:6px 8px;border-radius:4px}
#live b{display:block;font-size:11px;color:#888;font-weight:normal}
.bad{color:#f66}
form{display:flex;gap:6px;flex-wrap:wrap}
input{flex:1;min-width:140px;font:14px monospace;padding:6px;background:#000;color:#ddd;border:1px solid #444}
button{padding:6px 10px;background:#333;color:#ddd;border:1px solid #555;cursor:pointer}
pre{background:#000;padding:8px;height:50vh;overflow:auto;white-space:pre-wrap;margin-top:8px}
</style></head><body>
<h1>Flight computer — WiFi bench</h1>
<div id="live">waiting for /sample…</div>
<form id="f"><input id="c" placeholder="command (HELP)" autocomplete="off" autocapitalize="characters">
<button>Send</button></form>
<div style="margin-top:6px">
<button onclick="run('SCAN')">SCAN</button> <button onclick="run('ID')">ID</button>
<button onclick="run('SELFTEST')">SELFTEST</button> <button onclick="run('BATT')">BATT</button>
<button onclick="run('LOGS')">LOGS</button> <button onclick="run('BUZZER PASS')">BEEP</button>
<button onclick="run('HELP')">HELP</button></div>
<pre id="o"></pre>
<script>
const o=document.getElementById('o');
async function run(c){o.textContent+='> '+c+'\n';try{const r=await fetch('/cmd?c='+encodeURIComponent(c));
o.textContent+=await r.text();}catch(e){o.textContent+='(request failed)\n';}o.scrollTop=o.scrollHeight;}
document.getElementById('f').onsubmit=e=>{e.preventDefault();const i=document.getElementById('c');if(i.value)run(i.value);i.value='';};
function cell(k,v,bad){return '<div'+(bad?' class="bad"':'')+'><b>'+k+'</b>'+v+'</div>';}
async function poll(){try{const s=await (await fetch('/sample')).json();
document.getElementById('live').innerHTML=
cell('pressure',s.pressure_pa.toFixed(1)+' Pa',!s.baro_valid)+cell('temp',s.temperature_c.toFixed(2)+' °C',!s.baro_valid)+
cell('alt AGL',s.altitude_agl_m.toFixed(2)+' m',!s.baro_valid)+
cell('accel g',s.accel_x_g.toFixed(2)+', '+s.accel_y_g.toFixed(2)+', '+s.accel_z_g.toFixed(2),!s.accel_valid)+
cell('|accel|',s.accel_mag_g.toFixed(3)+' g',!s.accel_valid)+
cell('battery',s.batt_valid?s.batt_voltage_v.toFixed(2)+' V ('+s.batt_percent+'%)':'no reading',!s.batt_valid||s.batt_low)+
cell('uptime',(s.uptime_ms/1000).toFixed(0)+' s',false)+cell('sensors',s.sensors_up?'up':'INIT failed',!s.sensors_up);
}catch(e){}setTimeout(poll,500);}
poll();
</script></body></html>)HTML";

void handleIndex() { g_server.send_P(200, "text/html", INDEX_HTML); }

void handleSample() {
  SensorSample s = sensors_read();
  char buf[512];
  int n = snprintf(
      buf, sizeof(buf),
      "{\"uptime_ms\":%lu,\"sensors_up\":%s,"
      "\"baro_valid\":%s,\"accel_valid\":%s,"
      "\"pressure_pa\":%.2f,\"temperature_c\":%.2f,\"altitude_agl_m\":%.2f,"
      "\"accel_x_g\":%.3f,\"accel_y_g\":%.3f,\"accel_z_g\":%.3f,\"accel_mag_g\":%.3f,"
      "\"batt_valid\":%s,\"batt_voltage_v\":%.3f,\"batt_percent\":%u,\"batt_low\":%s}",
      static_cast<unsigned long>(millis()), g_sensorsUp ? "true" : "false",
      s.baro_valid ? "true" : "false", s.accel_valid ? "true" : "false",
      static_cast<double>(s.pressure_pa), static_cast<double>(s.temperature_c),
      static_cast<double>(s.altitude_agl_m),
      static_cast<double>(s.accel_x_g), static_cast<double>(s.accel_y_g),
      static_cast<double>(s.accel_z_g), static_cast<double>(s.accel_mag_g),
      battery_valid() ? "true" : "false", static_cast<double>(battery_voltage()),
      static_cast<unsigned>(battery_percent()), battery_low() ? "true" : "false");
  if (n < 0 || static_cast<size_t>(n) >= sizeof(buf)) {
    g_server.send(500, "application/json", "{\"ok\":false,\"reason\":\"sample_json_truncated\"}");
    return;
  }
  g_server.send(200, "application/json", buf);
}

void handleCmd() {
  if (!g_server.hasArg("c")) {
    g_server.send(400, "text/plain", "usage: /cmd?c=<command>   (try /cmd?c=HELP)\n");
    return;
  }
  String c = g_server.arg("c");
  Serial.print(F("[wifi] cmd: "));
  Serial.println(c);
  StreamString body;
  handleCommand(c, body, /*fromSerial=*/false);
  g_server.send(200, "text/plain", body);
}

// Same contract as the flight firmware's GET /log?n=7 (wireless.cpp).
void handleLog() {
  long n = g_server.hasArg("n") ? g_server.arg("n").toInt() : 0;
  File f = (n > 0 && n <= 999) ? logger_openForRead(static_cast<uint16_t>(n)) : File();
  if (!f) {
    g_server.send(404, "application/json", "{\"ok\":false,\"reason\":\"no_such_log\"}");
    return;
  }
  char disposition[64];
  snprintf(disposition, sizeof(disposition), "attachment; filename=\"FLIGHT%03ld.CSV\"", n);
  g_server.sendHeader("Content-Disposition", disposition);
  g_server.streamFile(f, "text/csv");
  f.close();
}

void handleNotFound() {
  g_server.send(404, "text/plain", "not found — try / , /sample , /cmd?c=HELP , /log?n=1\n");
}

void bringApUp() {
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1), IPAddress(255, 255, 255, 0));
  bool ok = WiFi.softAP(WIFI_AP_SSID, WIFI_AP_PASSWORD, WIFI_AP_CHANNEL, /*hidden=*/0, WIFI_AP_MAX_CONNECTIONS);

  g_server.on("/", HTTP_GET, handleIndex);
  g_server.on("/sample", HTTP_GET, handleSample);
  g_server.on("/cmd", HTTP_ANY, handleCmd);
  g_server.on("/log", HTTP_GET, handleLog);
  g_server.onNotFound(handleNotFound);
  g_server.begin();

  Serial.print(ok ? F("[wifi] AP up: \"") : F("[wifi] AP FAILED to start: \""));
  Serial.print(WIFI_AP_SSID);
  Serial.print(F("\"  ->  http://"));
  Serial.println(WiFi.softAPIP());
}

} // namespace

void setup() {
  // Buzzer pin LOW first, before Serial — same ordering as main.cpp.
  buzzer_init();

  battery_init();

  Serial.begin(115200);
  delay(200);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL); // sensors_init() re-calls this harmlessly

  Serial.println(F("\n[bench] WiFi bench console ready"));
  cmdPins(Serial);
  cmdScan(Serial);
  cmdInit(Serial); // auto, so /sample has live data from the first page load
  // Mount only (no new FLIGHTnnn.CSV) so LOGS and /log?n= work straight away;
  // FLASH still opens a file + writes a test record when you want that.
  logger_mount();

  // Radio last, after the sensor/flash init window — as main.cpp does.
  bringApUp();
  buzzer_setPattern(g_sensorsUp ? BuzzerPattern::SELF_TEST_PASS : BuzzerPattern::SELF_TEST_FAIL);
  Serial.println(F("[bench] join the AP and open http://192.168.4.1/  — or type HELP here."));
}

void loop() {
  pollSerialCommands();

  buzzer_update();
  battery_update();


  g_server.handleClient();

  if (g_streaming && (millis() - g_lastStreamAt >= BENCH_STREAM_INTERVAL_MS)) {
    g_lastStreamAt = millis();
    printSample(Serial, sensors_read());
  }
}
