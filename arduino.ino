// Pin Definitions for all sensors
#define Trig_Pin 9
#define Echo_Pin 11
#define Mic_Pin A0
#define Touch_Pin A1

float lastValidDistance = 0;

void setup() {
  Serial.begin(9600);
  
  pinMode(Trig_Pin, OUTPUT);
  pinMode(Echo_Pin, INPUT);
  pinMode(Mic_Pin, INPUT);
  pinMode(Touch_Pin, INPUT_PULLUP);
}

void loop() {
  long duration;
  float distanceCm;

  // Clear the trigPin
  digitalWrite(Trig_Pin, LOW);
  delayMicroseconds(2);

  // Send the 10µs trigger pulse
  digitalWrite(Trig_Pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(Trig_Pin, LOW);

  // Read echoPin with a timeout (30 ms = ~5 meters max)
  duration = pulseIn(Echo_Pin, HIGH, 30000);

  // If no echo received
  if (duration == 0) {
    Serial.print("[SENSOR]: ");
    Serial.print(lastValidDistance);
    Serial.println(" cm");
    delay(500);
    return;
  }

  // Calculate distance in cm
  distanceCm = duration * 0.034 / 2;

  // If valid, store and print
  if (distanceCm >= 2 && distanceCm <= 400) {
    lastValidDistance = distanceCm;
    Serial.print("[SENSOR]: ");
    Serial.print(distanceCm);
    Serial.println(" cm");
  } else {
    Serial.print("[SENSOR]: ");
    Serial.print(lastValidDistance);
    Serial.println(" cm");
  }

  // Read sound and touch sensor values
  int soundLevel = analogRead(Mic_Pin);
  int touchValue = digitalRead(Touch_Pin); 

  // Print sensor values
  Serial.print("[SOUND]: ");
  Serial.println(abs((soundLevel - 1011) * -1));
  Serial.print("[TOUCH]: ");
  Serial.println(touchValue);  

  delay(100);
}
