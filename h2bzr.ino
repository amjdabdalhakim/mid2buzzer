#include "melody.h"
#define REST 0

const byte bzrPin = 5;
const byte btnPin = 3;
byte debounce = 0;

int noteIndex = 0;
int melodyLength = sizeof(melody) / sizeof(melody[0]);
bool button = HIGH;

void setup() {
  pinMode(bzrPin, OUTPUT);
  pinMode(btnPin, INPUT_PULLUP);
}

void loop() {
  if(debounce >= 100){
      button = digitalRead(btnPin);
      debounce = 0;
      }
  else{
      debounce++;
    }

  if (button == LOW) {
    int freq = melody[noteIndex];
    if (freq == REST) {
      noTone(bzrPin);
    } else {
      tone(bzrPin, freq);
    }
    delay(noteDuration[noteIndex]);
    noTone(bzrPin);

    noteIndex = (noteIndex + 1) % melodyLength;
  } else {
    noteIndex = 0;
    noTone(bzrPin);
  }
}
