// AI-assisted interview prototype. Not compiled or bench-verified.
// Target: original ESP32-WROOM DevKit, ADC1 GPIO34.
#include <Arduino.h>
#include <math.h>
constexpr int PIN = 34;
// Replace with measured rail/resistor and identified NTC datasheet values.
constexpr float VS_MV=3200.0f, RF=10000.0f, R25=10000.0f, BETA=3950.0f;
const char* thermal="NORMAL";
uint32_t last=0;
void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN, ADC_11db);
  Serial.println("ms,mv,temp_c,status");
}
void loop() {
  if ((uint32_t)(millis()-last)<200) return;
  last=millis();
  float mv=0;
  for(int i=0;i<16;i++) { mv+=analogReadMilliVolts(PIN); delay(1); }
  mv/=16;
  const char* status;
  float t=NAN;
  if(mv<=100) {status="LOW_FAULT"; thermal="NORMAL";}
  else if(mv>=2900) {status="HIGH_FAULT"; thermal="NORMAL";}
  else {
    float r=RF*mv/(VS_MV-mv);
    t=1.0f/(1.0f/298.15f+logf(r/R25)/BETA)-273.15f;
    if(!isfinite(t) || t<15 || t>55) {
      status="OUT_OF_RANGE"; thermal="NORMAL";
    } else {
      if(t>=45) thermal="HOT";
      else if(t<=43) thermal="NORMAL";
      status=thermal;
    }
  }
  Serial.printf("%lu,%.2f,",(unsigned long)last,mv);
  if(isfinite(t)) Serial.printf("%.3f",t);
  Serial.printf(",%s\n",status);
}
