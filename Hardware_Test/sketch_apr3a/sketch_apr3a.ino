const int 
UART_RX_PIN = 16, 
UART_TX_PIN = 17;

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
}

void loop() {
  if (Serial2.available() > 0){
    String url = Serial2.readStringUntil('\n');
    Serial.println(url);
  }
}
