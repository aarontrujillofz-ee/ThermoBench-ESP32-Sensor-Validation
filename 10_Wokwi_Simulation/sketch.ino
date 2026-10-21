// ThermoBench - Wokwi ESP32 / NTC temperature firmware demonstrator
// Uses Wokwi's 3-pin NTC module (10k NTC + built-in 10k divider).
// NOT a simulation of the separate R1=9.82k, R2=990R, C1=100nF KiCad circuit.
// Output: ms,mv,temp_c,status  (a four-column CSV stream)

#include <Arduino.h>
#include <math.h>

constexpr int NTC_PIN = 34;                 // ESP32 ADC1 GPIO34
constexpr int ADC_SAMPLES = 16;
constexpr uint32_t SAMPLE_PERIOD_MS = 200; // 5 reports per second
constexpr float ADC_MAX_COUNTS = 4095.0f; // ESP32 12-bit ADC
constexpr float SUPPLY_MV = 3300.0f;      // Nominal Wokwi module supply
constexpr float R_FIXED_OHMS = 10000.0f; // Wokwi NTC module's internal resistor
constexpr float R_NTC_AT_25C = 10000.0f;
constexpr float BETA = 3950.0f;
constexpr float T_25_KELVIN = 298.15f;

uint32_t lastReportMs = 0;
bool hotLatched = false;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(NTC_PIN, ADC_11db);
  Serial.println("ms,mv,temp_c,status");
}

void loop() {
  const uint32_t now = millis();
  if ((uint32_t)(now - lastReportMs) < SAMPLE_PERIOD_MS) {
    return;
  }
  lastReportMs = now;

  uint32_t sumCounts = 0;
  for (int i = 0; i < ADC_SAMPLES; ++i) {
    sumCounts += analogRead(NTC_PIN);
    delay(1);
  }
  const float avgCounts = (float)sumCounts / ADC_SAMPLES;
  const float fraction = avgCounts / ADC_MAX_COUNTS;
  const float mv = fraction * SUPPLY_MV;

  float tempC = NAN;
  const char *status = "NORMAL";

  if (fraction <= 0.0f || mv <= 100.0f) {
    status = "LOW_FAULT";
    hotLatched = false;
  } else if (fraction >= 1.0f || mv >= 2900.0f) {
    status = "HIGH_FAULT";
    hotLatched = false;
  } else {
    // Wokwi NTC module: fixed 10k to VCC, NTC to GND.
    // Ratio = V(OUT)/VCC. This conversion matches Wokwi's NTC docs.
    const float rNTC = R_FIXED_OHMS * fraction / (1.0f - fraction);
    const float inverseT = (1.0f / T_25_KELVIN)
                         + (logf(rNTC / R_NTC_AT_25C) / BETA);
    tempC = (1.0f / inverseT) - 273.15f;

    if (!isfinite(tempC) || tempC < 15.0f || tempC > 55.0f) {
      status = "OUT_OF_RANGE";
      hotLatched = false;
    } else {
      if (tempC >= 45.0f) {
        hotLatched = true;
      } else if (tempC <= 43.0f) {
        hotLatched = false;
      }
      status = hotLatched ? "HOT" : "NORMAL";
    }
  }

  Serial.printf("%lu,%.2f,", (unsigned long)now, mv);
  if (isfinite(tempC)) {
    Serial.printf("%.3f", tempC);
  } else {
    Serial.print("nan");
  }
  Serial.printf(",%s\n", status);
}
