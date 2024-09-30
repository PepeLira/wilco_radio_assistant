#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <cstring>
#include <cstdlib>
#include <cstdint>
#include <cmath>
#include <csignal>
#include <chrono>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

// External libraries
#include <sndfile.h>  // For writing WAV files
#include <fftw3.h>    // For FFT (optional, can be omitted if not used)

#define BUFFER_SIZE 16384  // Buffer size in bytes

// Global flag for handling Ctrl+C
volatile sig_atomic_t stop_flag = 0;
void handle_signal(int signal) {
    stop_flag = 1;
}

// Function prototypes
bool connect_to_server(int &sockfd, const std::string &ip, int port);
void set_sample_rate(int sockfd, uint32_t sample_rate);
void set_center_freq(int sockfd, uint32_t freq);
void set_gain_mode(int sockfd, uint8_t mode);
void set_agc_mode(int sockfd, uint8_t mode);
void fm_demodulate(const std::vector<std::complex<float>> &iq_samples, std::vector<float> &audio_samples);
void write_wav_file(const std::string &filename, const std::vector<float> &audio_data, int sample_rate);

int main() {
    // Register signal handler for graceful shutdown
    std::signal(SIGINT, handle_signal);

    std::string IP = "127.0.0.1";  // Replace with your rtl_tcp server IP address
    int PORT = 1234;               // Replace with your rtl_tcp server port

    int sockfd;
    if (!connect_to_server(sockfd, IP, PORT)) {
        std::cerr << "Failed to connect to " << IP << ":" << PORT << std::endl;
        return EXIT_FAILURE;
    }

    // Configure SDR settings
    uint32_t sample_rate = 2048000;    // Sample rate in Hz
    uint32_t center_freq = 88900000;  // Center frequency in Hz (adjust to a local FM station)
    set_sample_rate(sockfd, sample_rate);
    set_center_freq(sockfd, center_freq);
    set_gain_mode(sockfd, 0);  // 0 = auto gain, 1 = manual gain
    set_agc_mode(sockfd, 1);   // 0 = off, 1 = on

    // Prepare to receive and process data
    int audio_rate = 44100;  // Audio sample rate
    int duration = 50;       // Duration to record in seconds
    int total_samples = sample_rate * duration;
    int num_buffers = total_samples / (BUFFER_SIZE / 2);  // Each IQ sample is 2 bytes (I and Q each 8 bits)

    std::vector<float> audio_data;
    audio_data.reserve(duration * audio_rate);

    std::cout << "Starting data reception for " << duration << " seconds." << std::endl;

    auto start_time = std::chrono::steady_clock::now();

    for (int i = 0; i < num_buffers && !stop_flag; ++i) {
        std::vector<uint8_t> buffer(BUFFER_SIZE);
        ssize_t bytes_received = recv(sockfd, buffer.data(), BUFFER_SIZE, MSG_WAITALL);
        if (bytes_received != BUFFER_SIZE) {
            std::cerr << "Incomplete data received. Expected " << BUFFER_SIZE << " bytes, got " << bytes_received << " bytes." << std::endl;
            break;
        }

        // Convert raw bytes to IQ samples
        size_t num_samples = bytes_received / 2;
        std::vector<std::complex<float>> iq_samples(num_samples);
        for (size_t j = 0; j < num_samples; ++j) {
            float I = static_cast<float>(buffer[2 * j]) - 127.5f;
            float Q = static_cast<float>(buffer[2 * j + 1]) - 127.5f;
            iq_samples[j] = std::complex<float>(I, Q);
        }

        // FM Demodulation
        std::vector<float> demodulated_samples;
        fm_demodulate(iq_samples, demodulated_samples);

        // Append audio data
        audio_data.insert(audio_data.end(), demodulated_samples.begin(), demodulated_samples.end());

        // Check if duration has been reached
        auto current_time = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(current_time - start_time).count() >= duration) {
            std::cout << "Desired recording duration reached." << std::endl;
            break;
        }
    }

    // Close the socket
    close(sockfd);
    std::cout << "Socket closed." << std::endl;

    // Resample and save audio data to WAV file
    write_wav_file("recorded_audio.wav", audio_data, audio_rate);
    std::cout << "Audio data saved to recorded_audio.wav" << std::endl;

    return EXIT_SUCCESS;
}

bool connect_to_server(int &sockfd, const std::string &ip, int port) {
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return false;
    }

    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr) <= 0) {
        perror("Invalid address");
        return false;
    }

    std::cout << "Connecting to " << ip << ":" << port << std::endl;
    if (connect(sockfd, reinterpret_cast<sockaddr *>(&serv_addr), sizeof(serv_addr)) < 0) {
        perror("Connection failed");
        return false;
    }

    std::cout << "Connection established." << std::endl;
    return true;
}

void send_command(int sockfd, uint8_t cmd, uint32_t param) {
    uint8_t buffer[5];
    buffer[0] = cmd;
    buffer[1] = (param >> 24) & 0xFF;
    buffer[2] = (param >> 16) & 0xFF;
    buffer[3] = (param >> 8) & 0xFF;
    buffer[4] = param & 0xFF;
    ssize_t bytes_sent = send(sockfd, buffer, 5, 0);
    if (bytes_sent != 5) {
        std::cerr << "Failed to send command 0x" << std::hex << static_cast<int>(cmd) << std::dec << std::endl;
    }
}

void set_sample_rate(int sockfd, uint32_t sample_rate) {
    send_command(sockfd, 0x02, sample_rate);
    std::cout << "Set sample rate to " << sample_rate << " Hz" << std::endl;
}

void set_center_freq(int sockfd, uint32_t freq) {
    send_command(sockfd, 0x01, freq);
    std::cout << "Set center frequency to " << freq << " Hz" << std::endl;
}

void set_gain_mode(int sockfd, uint8_t mode) {
    send_command(sockfd, 0x03, mode);
    std::cout << "Set gain mode to " << (mode == 0 ? "auto" : "manual") << std::endl;
}

void set_agc_mode(int sockfd, uint8_t mode) {
    send_command(sockfd, 0x06, mode);
    std::cout << "Set AGC mode to " << (mode == 0 ? "off" : "on") << std::endl;
}

void fm_demodulate(const std::vector<std::complex<float>> &iq_samples, std::vector<float> &audio_samples) {
    size_t num_samples = iq_samples.size();
    audio_samples.resize(num_samples - 1);

    for (size_t i = 1; i < num_samples; ++i) {
        std::complex<float> prev = iq_samples[i - 1];
        std::complex<float> curr = iq_samples[i];
        float demod = std::arg(curr * std::conj(prev));
        audio_samples[i - 1] = demod;
    }

    // Optional: Low-pass filter and downsample to audio rate
    // Skipping filtering and resampling for simplicity
}

void write_wav_file(const std::string &filename, const std::vector<float> &audio_data, int sample_rate) {
    // Normalize audio data
    float max_value = 0.0f;
    for (float val : audio_data) {
        if (std::abs(val) > max_value) {
            max_value = std::abs(val);
        }
    }
    std::vector<short> audio_int16(audio_data.size());
    if (max_value > 0.0f) {
        for (size_t i = 0; i < audio_data.size(); ++i) {
            audio_int16[i] = static_cast<short>((audio_data[i] / max_value) * 32767);
        }
    }

    // Configure WAV file parameters
    SF_INFO sf_info{};
    sf_info.samplerate = sample_rate;
    sf_info.channels = 1;
    sf_info.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;

    SNDFILE *outfile = sf_open(filename.c_str(), SFM_WRITE, &sf_info);
    if (!outfile) {
        std::cerr << "Error opening output file: " << sf_strerror(nullptr) << std::endl;
        return;
    }

    sf_count_t frames_written = sf_write_short(outfile, audio_int16.data(), audio_int16.size());
    if (frames_written != static_cast<sf_count_t>(audio_int16.size())) {
        std::cerr << "Error writing audio data to file." << std::endl;
    }

    sf_close(outfile);
}

