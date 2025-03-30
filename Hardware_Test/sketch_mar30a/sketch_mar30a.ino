#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <DHT.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi Credentials
const char* ssid = "UGM eduroam";
const char* password = "moyf7667";

// MQTT Configuration
const char* mqtt_broker = "broker.emqx.io";
const char* mqtt_client_id = "sic6_prototype_esp32";
const char* mqtt_topic_pub = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor";
WiFiClient espClient;
PubSubClient client(espClient);

// Servo setup
Servo servoYaw;
Servo servoPitch;
const int SERVO_YAW_PIN = 2;
const int SERVO_PITCH_PIN = 15;

// DHT11 setup
#define DHTPIN 23
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ADS1115 setup
Adafruit_ADS1115 ads;

// UART communication setup
const int UART_RX_PIN = 16;
const int UART_TX_PIN = 17;

// Sensor Thresholds
const int THRESHOLD_KY026 = 1000;
const int THRESHOLD_MQ135 = 4000;
const int THRESHOLD_MQ7 = 7000;
const float THRESHOLD_TEMPERATURE = 40.0;
const int RELAY_PIN = 5;
bool fireTriggered = false;

// Function to connect to WiFi
void setupWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
}

// Function to connect to MQTT broker
void setupMQTT() {
  client.setServer(mqtt_broker, 1883);
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(mqtt_client_id)) {
      Serial.println("Connected to MQTT!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Trying again in 5 seconds...");
      delay(5000);
    }
  }
}

// Function to read sensors and publish data
void readSensors() {
  int sensorMQ7 = ads.readADC_SingleEnded(1);
  int sensorMQ135 = ads.readADC_SingleEnded(2);
  int sensorKY026 = ads.readADC_SingleEnded(3);
  float temperature = dht.readTemperature();
  
  Serial.print("MQ7: "); Serial.print(sensorMQ7);
  Serial.print(" | MQ135: "); Serial.print(sensorMQ135);
  Serial.print(" | KY-026: "); Serial.print(sensorKY026);
  Serial.print(" | Suhu: "); Serial.println(temperature);
  
  fireTriggered = (sensorKY026 > THRESHOLD_KY026 && sensorMQ135 > THRESHOLD_MQ135 &&
                   sensorMQ7 > THRESHOLD_MQ7 && temperature > THRESHOLD_TEMPERATURE);
  
  // Publish sensor data to MQTT
  char payload[150];
  // snprintf(payload, sizeof(payload), "{\"MQ7\":%d,\"MQ135\":%d,\"KY026\":%d,\"Temp\":%.2f,\"status\":\"%d\"}",
          // sensorMQ7, sensorMQ135, sensorKY026, temperature, fireTriggered ? 1 : 0);
  snprintf(payload, sizeof(payload), "{\"MQ7\":%d,\"MQ135\":%d,\"KY026\":%d,\"Temp\":%.2f,\"status\":\"%d\"}",
        sensorMQ7, sensorMQ135, sensorKY026, temperature, 1);
  client.publish(mqtt_topic_pub, payload);
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  Wire.begin();
  ads.begin();
  dht.begin();
  pinMode(RELAY_PIN, OUTPUT);
  servoYaw.attach(SERVO_YAW_PIN);
  servoPitch.attach(SERVO_PITCH_PIN);
  // servoYaw.write(90);
  // servoPitch.write(145);
  
  setupWiFi();
  setupMQTT();
  Serial.println("Sistem Bombatronic siap");
}

void loop() {
  if (!client.connected()) {
    setupMQTT();
  }
  client.loop();
  readSensors();
  delay(1000); // Publish every second
}
