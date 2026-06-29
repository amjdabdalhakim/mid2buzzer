# mid2buzzer 🎵

A hardware-software pipeline that parses monophonic MIDI files and converts them into C++ arrays to be played on a physical piezo buzzer using an Arduino.

## 🚀 How It Works
1. **Python Parser (`mid2h.py`):** Reads a `.mid` file, calculates frequencies (Hz) using the formula $440.0 \times 2.0^{\frac{note - 69}{12.0}}$, processes track events, and exports `melody.h`.
2. **Arduino Firmware (`h2bzr.ino`):** Uses a debounced button interface to play through the frequencies and note durations step-by-step using PWM generation (`tone()`).

## 🛠️ Tech Stack
* **Python** (MIDI processing, File I/O, Data Manipulation)
* **C / C++** (Arduino Firmware, Memory Management, Embedded Logic)

## 📦 How to Use
1. Run the script: `python3 mid2h.py yourfile.mid`
2. Move the generated `melody.h` into your Arduino sketch folder.
3. Flash `h2bzr.ino` to your microcontroller and connect a buzzer to Pin 5 and a button to Pin 3.
