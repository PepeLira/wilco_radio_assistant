import socket
import numpy as np
import struct
import logging
import time
from scipy.signal import lfilter, butter, resample
from scipy.io.wavfile import write

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    IP = '127.0.0.1'  # Replace with your rtl_tcp server IP address
    PORT = 1234       # Replace with your rtl_tcp server port

    BUFFER_SIZE = 16384  # Buffer size in bytes
    sdr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    logging.info(f'Connecting to {IP}:{PORT}')
    try:
        sdr_socket.connect((IP, PORT))
        logging.info('Connection established.')
    except Exception as e:
        logging.error(f'Failed to connect to {IP}:{PORT}. Error: {e}')
        return

    # Configure SDR settings
    sample_rate = 2_048_000  # Sample rate in Hz
    center_freq = 88_900_000  # Center frequency in Hz (adjust to a local FM station)
    set_sample_rate(sdr_socket, sample_rate)
    set_center_freq(sdr_socket, center_freq)
    set_gain_mode(sdr_socket, 0)  # 0 = auto gain, 1 = manual gain
    set_agc_mode(sdr_socket, 1)   # 0 = off, 1 = on

    # Prepare to receive and process data
    audio_rate = 44100  # Audio sample rate
    duration = 50       # Duration to record in seconds
    total_samples = int(sample_rate * duration)
    num_buffers = total_samples // (BUFFER_SIZE // 2)  # Each IQ sample is 2 bytes

    # Initialize arrays to store audio data
    audio_data = np.array([], dtype=np.float32)

    start_time = time.time()
    logging.info(f'Starting data reception for {duration} seconds.')
    
    try:
        for _ in range(num_buffers):
            data = sdr_socket.recv(BUFFER_SIZE)
            if not data:
                logging.warning('No data received from the socket.')
                break

            # Convert raw bytes to numpy array
            iq_data = np.frombuffer(data, dtype=np.uint8)
            # Normalize data to range -127.5 to +127.5
            iq_data = iq_data.astype(np.float32) - 127.5

            # Separate I and Q components
            I = iq_data[::2]
            Q = iq_data[1::2]

            # Create complex IQ signal
            complex_signal = I + 1j * Q

            # FM Demodulation
            demodulated = fm_demodulate(complex_signal)

            # Low-pass filter and downsample to audio rate
            audio_chunk = downsample_audio(demodulated, sample_rate, audio_rate)

            # Append audio data
            audio_data = np.concatenate((audio_data, audio_chunk))

            # Check if duration has been reached
            if time.time() - start_time >= duration:
                logging.info('Desired recording duration reached.')
                break

        # Save audio data to WAV file
        write_audio_file('recorded_audio.wav', audio_rate, audio_data)
        logging.info('Audio data saved to recorded_audio.wav')

    except KeyboardInterrupt:
        logging.info("Streaming stopped by user.")
    except Exception as e:
        logging.error(f'An error occurred: {e}')
    finally:
        sdr_socket.close()
        logging.info('Socket closed.')

def set_sample_rate(sock, sample_rate):
    # Command 0x02: Set sample rate (unsigned 32-bit integer)
    cmd = struct.pack('>BI', 0x02, sample_rate)
    sock.sendall(cmd)
    logging.info(f'Set sample rate to {sample_rate} Hz')

def set_center_freq(sock, freq):
    # Command 0x01: Set center frequency (unsigned 32-bit integer)
    cmd = struct.pack('>BI', 0x01, freq)
    sock.sendall(cmd)
    logging.info(f'Set center frequency to {freq} Hz')

def set_gain_mode(sock, mode):
    # Command 0x03: Set gain mode (0 = auto, 1 = manual)
    cmd = struct.pack('>BI', 0x03, mode)
    sock.sendall(cmd)
    logging.info(f'Set gain mode to {"auto" if mode == 0 else "manual"}')

def set_agc_mode(sock, mode):
    # Command 0x06: Set AGC mode (0 = off, 1 = on)
    cmd = struct.pack('>BI', 0x06, mode)
    sock.sendall(cmd)
    logging.info(f'Set AGC mode to {"on" if mode == 1 else "off"}')

def fm_demodulate(complex_signal):
    # FM demodulation
    phase = np.angle(complex_signal)
    demodulated = np.diff(np.unwrap(phase))
    return demodulated

def downsample_audio(demodulated_signal, sdr_rate, audio_rate):
    # Design a low-pass filter
    cutoff_freq = 100e3  # 100 kHz cutoff for FM
    b, a = butter(5, cutoff_freq / (sdr_rate / 2), btype='low')
    filtered = lfilter(b, a, demodulated_signal)

    # Resample to audio_rate
    num_samples = int(len(filtered) * audio_rate / sdr_rate)
    resampled_audio = resample(filtered, num_samples)
    return resampled_audio.astype(np.float32)

def write_audio_file(filename, rate, audio_data):
    # Normalize audio_data to int16 range
    audio_data = audio_data / np.max(np.abs(audio_data))  # Normalize to -1 to +1
    audio_int16 = np.int16(audio_data * 32767)
    write(filename, rate, audio_int16)

if __name__ == '__main__':
    main()
