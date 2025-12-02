// pino de controle do rele
#define RELE_1  7

void setup() {
  Serial.begin(9600);
  
  // define o pino do rele como uma saída
  pinMode(RELE_1, OUTPUT);
  // inicia com o rele desligado
  digitalWrite(RELE_1, HIGH);
}

void loop() {
  // chegou algum comando na porta serial?
  if (Serial.available()) {
    char comando = (char) Serial.read();
    printf("recebido %c", &comando);

    if (comando == 'L') {
      digitalWrite(RELE_1, LOW);
    } else if (comando == 'D') {
      digitalWrite(RELE_1, HIGH);   
    }
  }  

  delay(500);
}
