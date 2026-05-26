#define N_COEF 3 //Defines number of coefficients for a biquad filter
#define SHIFT_VAL 14 // Division by 16384 via bit-shifting

int32_t b_coef[N_COEF] = {16384, -32768, 16384};// for feedforward
int32_t a_coef[N_COEF] = {16384, -31129, 14786}; // for feedback

int32_t w[N_COEF] = {0, 0, 0};

//arduino input pin
const int MIC_PIN = A0;

void setup() {
  Serial.begin(115200);
  pinMode(MIC_PIN, INPUT);
}

void loop() {
  int32_t input_sample = analogRead(MIC_PIN);
  w[0] = input_sample; 
  
  // Feedback branch
  for (int i = 1; i < N_COEF; i++) {
      w[0] -= (a_coef[i] * w[i]) >> SHIFT_VAL;
  }
  // Feedforward branch
  int32_t out_accum = 0;
  for (int i = 0; i < N_COEF; i++) {
      out_accum += (b_coef[i] * w[i]) >> SHIFT_VAL;
  }
  
  int16_t output_sample = (int16_t)out_accum;

  // Shift delay 
  for (int i = N_COEF - 1; i > 0; i--) {
      w[i] = w[i-1];
  }
  Serial.print(input_sample);
  Serial.print(",");
  Serial.println(output_sample);

  delayMicroseconds(125); 
}