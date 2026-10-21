// ThermoBench / Wokwi ESP32 NTC firmware demonstrator
// Newly prepared virtual test sketch, NOT the verified hardware firmware.
// Wokwi's 10k/10k NTC module is connected DIRECTLY to ESP32 GPIO34.
// The exact KiCad 9.82k divider / 990R / 100nF analog front end is NOT simulated.
// Firmware output is virtual/synthetic and cannot be used as hardware evidence.
#include <Arduino.h>
#include <math.h>

constexpr int NTC_ADC_PIN = 34;
constexpr float ADC_FULL_SCALE = 4095.0f;
constexpr float VCC_MV = 3300.0f; // nominal Wokwi module excitation, not hardware calibration
constexpr float R_FIXED_OHMS = 10000.0f; // internal resistor in Wokwi NTC module
constexpr float R_25C_OHMS = 10000.0f;
constexpr float NTC_BETA = 3950.0f;
constexpr uint32_t PERIOD_MS = 200;

uint32_t lastReading = 0;
bool hot = false;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(NTC_ADC_PIN, ADC_11db);
  Serial.println("ms,mv,temp_c,status");
}

void loop() {
  const uint32_t now = millis();
  if ((uint32_t)(now - lastReading) < PERIOD_MS) return;
  lastReading = now;

  float counts = 0.0f;
  for (int i = 0; i < 16; ++i) {
    counts += analogRead(NTC_ADC_PIN);
    delay(1);
  }
  counts /= 16.0f;

  // Wokwi analog ADC scaling is approximate: this is a nominal display voltage.
  const float mv = VCC_MV * (counts / ADC_FULL_SCALE);
  const char *status = "NORMAL";
  float tempC = NAN;

  if (mv <= 100.0f) {
    status = "LOW_FAULT";
    hot = false;
  } else if (mv >= 2900.0f) {
    status = "HIGH_FAULT";
    hot = false;
  } else {
    const float fraction = counts / ADC_FULL_SCALE;
    // Wokwi NTC module output model: NTC to GND, internal 10k to VCC.
    const float rNtc = R_FIXED_OHMS * fraction / (1.0f - fraction);
    tempC = 1.0f / (1.0f / 298.15f + logf(rNtc / R_25C_OHMS) / NTC_BETA) - 273.15f;

    if (!isfinite(tempC) || tempC < 15.0f || tempC > 55.0f) {
      status = "OUT_OF_RANGE";
      hot = false;
    } else {
      if (tempC >= 45.0f) hot = true;
      else if (tempC <= 43.0f) hot = false;
      status = hot ? "HOT" : "NORMAL";
    }
  }

  Serial.printf("%lu,%.2f,", (unsigned long)now, mv);
  if (isfinite(tempC)) Serial.printf("%.3f", tempC);
  Serial.printf(",%s\n", status);
}
