import mido
import sys 
from math import pow

# MIDI note to frequency (A4 = 440 Hz)
def midi_to_freq(note):
    if note < 0 or note > 127:
        return 0  # silence
    return round(440.0 * pow(2.0, (note - 69) / 12.0))

def midi_to_arrays(midi_file_path, ticks_per_beat=480, base_bpm=120, rest_symbol="REST"):
    """
    Convert a monophonic MIDI file to two C++ arrays: melody (frequencies) and durations (ms).
    
    Parameters:
        midi_file_path: path to the .mid file
        ticks_per_beat: default ticks per beat (if not found in file)
        base_bpm:        default tempo in BPM (if not in file)
        rest_symbol:     name of the 'rest' constant in your Arduino code
    
    Returns:
        (melody_str, duration_str) formatted C++ array strings.
    """
    mid = mido.MidiFile(midi_file_path)
    
    # Extract tempo from meta messages (microseconds per beat)
    tempo = 500000  # default 120 BPM
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
    
    # Use ticks_per_beat from file if available
    if mid.ticks_per_beat:
        ticks_per_beat = mid.ticks_per_beat
    
    # Time values in seconds per tick
    seconds_per_tick = (tempo / 1_000_000) / ticks_per_beat
    
    notes = []      # list of (frequency, duration_in_ticks)
    current_time = 0
    
    # Merge all tracks into one event list (sorted by absolute time)
    events = []
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if msg.type in ('note_on', 'note_off'):
                events.append((abs_time, msg))
    
    events.sort(key=lambda x: x[0])
    
    active_notes = {}  # note -> start_time (ticks)
    last_time = 0
    
    for abs_time, msg in events:
        # First, handle any time gap → rest if no notes active
        if abs_time > last_time and not active_notes:
            delta = abs_time - last_time
            if delta > 0:
                notes.append((0, delta))  # 0 = rest
        
        last_time = abs_time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            # If another note is already on, terminate it (avoids overlapping – force monophonic)
            if active_notes:
                start_time = min(active_notes.values())
                duration = abs_time - start_time
                freq = midi_to_freq(next(iter(active_notes)))
                notes.append((freq, duration))
                active_notes.clear()
            active_notes[msg.note] = abs_time
        
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_notes:
                start_time = active_notes.pop(msg.note)
                duration = abs_time - start_time
                freq = midi_to_freq(msg.note)
                notes.append((freq, duration))
    
    # Convert durations from ticks to milliseconds
    melody = []
    durations = []
    for freq, ticks in notes:
        melody.append(freq)
        duration_ms = round(ticks * seconds_per_tick * 1000)
        durations.append(duration_ms if duration_ms > 0 else 1)  # minimum 1 ms
    
    # Build C++ array strings
    melody_str = "int melody[] = {\n    "
    melody_str += ", ".join(str(f) if f > 0 else rest_symbol for f in melody)
    melody_str += "\n};"
    
    duration_str = "int noteDuration[] = {\n    "
    duration_str += ", ".join(str(d) for d in durations)
    duration_str += "\n};"
    
    return melody_str, duration_str

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mid2h.py <yourfile.mid>")
        exit(1)

    melody, durations = midi_to_arrays(sys.argv[1])

    with open("melody.h", "w") as f:
        f.write(melody + "\n\n")
        f.write(durations + "\n")

    print("Saved to melody.h")