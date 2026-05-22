import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

# --- 1. Audio Stream Parameters ---
samp_freq = 16000
buffer_len = 256 # Number of frames per buffer
data_type = np.int16

# --- 2. Filter Setup & Global Variables ---
N_COEF = 3
HALF_MAX_VAL = 32768
GAIN = 1.0

# 2nd-order DC Blocker Biquad Coefficients
b_coef = [32768, -65536, 32768] 
a_coef = [32768, -62259, 29573]

# State variable for Direct Form 2
w = np.zeros(N_COEF, dtype=int)

# --- 3. Recording Storage ---
# These lists will store the full history of the audio for saving/plotting later
recorded_original = []
recorded_filtered = []

# --- 4. Biquad Processing Function ---
def process_df2(input_buffer, output_buffer, buffer_len):
    global w
    for n in range(buffer_len):
        
        # Apply input gain
        w[0] = int(GAIN * input_buffer[n])
        
        # TASK 4: Feedback
        for i in range(1, N_COEF):
            w[0] -= int((a_coef[i] * w[i]) / HALF_MAX_VAL)
            
        # TASK 5: Feedforward
        out_accum = 0
        for i in range(N_COEF):
            out_accum += int((b_coef[i] * w[i]) / HALF_MAX_VAL)
            
        # Write to output buffer (clamped safely to 16-bit limits)
        output_buffer[n] = np.clip(out_accum, -32768, 32767)
            
        # TASK 6: Shift delay line
        for i in reversed(range(1, N_COEF)):
            w[i] = w[i-1]

# --- 5. The Real-Time Audio Callback ---
def callback(indata, outdata, frames, time_info, status):
    if status:
        print(f"Status: {status}", flush=True)

    # Convert incoming audio chunk to integers
    in_buffer = indata[:, 0].astype(int)
    out_buffer = np.zeros(frames, dtype=int)
    
    # Process through the Direct Form 2 filter
    process_df2(in_buffer, out_buffer, frames)
    
    # SAVE THE DATA FOR LATER: Append the current chunk to our global recording lists
    recorded_original.extend(in_buffer.tolist())
    recorded_filtered.extend(out_buffer.tolist())
    
    # Route cleaned audio to the speakers
    outdata[:, 0] = out_buffer.astype(np.int16)

# --- 6. Main Execution ---
if __name__ == "__main__":
    test_duration_seconds = 7 

    print("="*50)
    print(f"🎙️ Starting Live Real-Time Biquad Filter Test...")
    print(f"Speak into your microphone for the next {test_duration_seconds} seconds!")
    print("="*50)

    # Reset state variable before running
    w.fill(0)

    try:
        # Open the audio stream
        with sd.Stream(samplerate=samp_freq, 
                       blocksize=buffer_len, 
                       dtype=data_type, 
                       channels=1, 
                       callback=callback):
            
            # Keep stream open for the set duration
            sd.sleep(test_duration_seconds * 1000)
            
        print("\n✅ Audio test completed successfully and hardware released.")
        
        # --- 7. Save to .wav Files ---
        print("💾 Saving audio to .wav files...")
        
        # Convert lists back to strict 16-bit numpy arrays
        final_original_audio = np.array(recorded_original, dtype=np.int16)
        final_filtered_audio = np.array(recorded_filtered, dtype=np.int16)
        
        wavfile.write("live_original.wav", samp_freq, final_original_audio)
        wavfile.write("live_filtered.wav", samp_freq, final_filtered_audio)
        print("   -> Saved 'live_original.wav' and 'live_filtered.wav' in your current folder.")
        
        # --- 8. Plot the Results ---
        print(" Generating plot...")
        ALPHA = 0.75
        plt.figure(figsize=(10, 4))
        
        # Create a time axis based on the length of the recording
        time_axis = np.arange(len(final_original_audio)) / samp_freq
        
        plt.plot(time_axis, final_original_audio, 'tab:blue', label="Original (Microphone)", alpha=ALPHA)
        plt.plot(time_axis, final_filtered_audio, 'tab:orange', label="Filtered (Output)", alpha=ALPHA)
        
        plt.title("Live Microphone Capture: Direct Form 2 Biquad Filter")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        plt.show()

    except Exception as e:
        print(f"\n An error occurred: {str(e)}")