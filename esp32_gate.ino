#include <WiFi.h>
#include <WebServer.h>

const char* SSID = "YOUR_WIFI";
const char* PASS = "YOUR_PASSWORD";
const char* KEY  = "CHANGE_ME";       // Set same value as ESP32_KEY in the environment
const int RELAY_PIN = 26;
const int OPEN_MS = 5000;             // gate kitni der khula rahe

WebServer server(80);

void handleOpen() {
  if (server.arg("key") != KEY) { server.send(403, "text/plain", "forbidden"); return; }
  digitalWrite(RELAY_PIN, HIGH);      // agar relay active-LOW hai to LOW/HIGH ulta kar do
  server.send(200, "text/plain", "opened");
  delay(OPEN_MS);
  digitalWrite(RELAY_PIN, LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(WiFi.localIP());     // ye IP config.py me daalna
  server.on("/open", handleOpen);
  server.begin();
}

void loop() { server.handleClient(); }
