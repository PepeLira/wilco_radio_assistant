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

// Librerías externas
#include <sndfile.h>  // Para escribir archivos WAV
// #include <samplerate.h> // Eliminado: No se usará

#define BUFFER_SIZE 16384  // Tamaño del búfer en bytes
#define DE_EMPHASIS_TIME_CONSTANT 75e-6  // Constante de tiempo para de-énfasis (75 µs para América)

// Indicador global para manejar Ctrl+C
volatile sig_atomic_t stop_flag = 0;
void handle_signal(int signal) {
    stop_flag = 1;
}

// Prototipos de funciones
bool connect_to_server(int &sockfd, const std::string &ip, int port);
void set_sample_rate(int sockfd, uint32_t sample_rate);
void set_center_freq(int sockfd, uint32_t freq);
void set_gain_mode(int sockfd, uint8_t mode);
void set_gain(int sockfd, uint32_t gain);
void set_agc_mode(int sockfd, uint8_t mode);
void set_rtl_agc_mode(int sockfd, uint8_t mode);
void fm_demodulate(const std::vector<std::complex<float>> &iq_samples, std::vector<float> &audio_samples);
void apply_de_emphasis(std::vector<float> &audio_samples, float sample_rate);
void apply_squelch(std::vector<float> &audio_samples, float squelch_level);
void resample_audio(const std::vector<float> &input_samples, std::vector<float> &output_samples, float input_rate, float output_rate);
void write_wav_file(const std::string &filename, const std::vector<float> &audio_data, int sample_rate);

int main() {
    // Registrar el manejador de señal para un apagado seguro
    std::signal(SIGINT, handle_signal);

    std::string IP = "127.0.0.1";  // Dirección IP del servidor rtl_tcp
    int PORT = 1234;               // Puerto del servidor rtl_tcp

    int sockfd;
    if (!connect_to_server(sockfd, IP, PORT)) {
        std::cerr << "No se pudo conectar a " << IP << ":" << PORT << std::endl;
        return EXIT_FAILURE;
    }

    // Configurar ajustes del SDR
    uint32_t sample_rate = 180000;       // Tasa de muestreo en Hz (180 kHz)
    uint32_t center_freq = 88900000;     // Frecuencia central en Hz (88.9 MHz)
    uint32_t gain = 500;                 // Ganancia en décimas de dB (50.0 dB)

    set_sample_rate(sockfd, sample_rate);
    set_center_freq(sockfd, center_freq);
    set_gain_mode(sockfd, 1);            // 0 = ganancia automática, 1 = manual
    set_gain(sockfd, gain);              // Establecer ganancia a 50.0 dB
    set_agc_mode(sockfd, 0);             // Deshabilitar AGC del sintonizador
    set_rtl_agc_mode(sockfd, 0);         // Deshabilitar RTL AGC

    // Preparar para recibir y procesar datos
    int audio_rate = 44100;  // Tasa de muestreo de audio
    int duration = 50;       // Duración de grabación en segundos
    int total_samples = sample_rate * duration;
    int num_buffers = total_samples / (BUFFER_SIZE / 2);  // Cada muestra IQ es de 2 bytes (I y Q de 8 bits cada uno)

    std::vector<float> audio_data;

    std::cout << "Iniciando recepción de datos durante " << duration << " segundos." << std::endl;

    auto start_time = std::chrono::steady_clock::now();

    for (int i = 0; i < num_buffers && !stop_flag; ++i) {
        std::vector<uint8_t> buffer(BUFFER_SIZE);
        ssize_t bytes_received = recv(sockfd, buffer.data(), BUFFER_SIZE, MSG_WAITALL);
        if (bytes_received != BUFFER_SIZE) {
            std::cerr << "Datos incompletos recibidos. Se esperaban " << BUFFER_SIZE << " bytes, se recibieron " << bytes_received << " bytes." << std::endl;
            break;
        }

        // Convertir bytes en muestras IQ
        size_t num_samples = bytes_received / 2;
        std::vector<std::complex<float>> iq_samples(num_samples);
        for (size_t j = 0; j < num_samples; ++j) {
            float I = static_cast<float>(buffer[2 * j]) - 127.5f;
            float Q = static_cast<float>(buffer[2 * j + 1]) - 127.5f;
            iq_samples[j] = std::complex<float>(I, Q);
        }

        // Demodulación FM (WFM)
        std::vector<float> demodulated_samples;
        fm_demodulate(iq_samples, demodulated_samples);

        // Aplicar squelch
        float squelch_level = 50.0f;  // Nivel de squelch
        apply_squelch(demodulated_samples, squelch_level);

        // Aplicar de-énfasis
        apply_de_emphasis(demodulated_samples, static_cast<float>(sample_rate));

        // Re-muestrear a la tasa de audio
        std::vector<float> resampled_audio;
        resample_audio(demodulated_samples, resampled_audio, static_cast<float>(sample_rate), static_cast<float>(audio_rate));

        // Agregar datos de audio
        audio_data.insert(audio_data.end(), resampled_audio.begin(), resampled_audio.end());

        // Verificar si se ha alcanzado la duración deseada
        auto current_time = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(current_time - start_time).count() >= duration) {
            std::cout << "Se alcanzó la duración de grabación deseada." << std::endl;
            break;
        }
    }

    // Cerrar el socket
    close(sockfd);
    std::cout << "Socket cerrado." << std::endl;

    // Guardar datos de audio en archivo WAV
    write_wav_file("recorded_audio.wav", audio_data, audio_rate);
    std::cout << "Datos de audio guardados en recorded_audio.wav" << std::endl;

    return EXIT_SUCCESS;
}

// Implementaciones de funciones

bool connect_to_server(int &sockfd, const std::string &ip, int port) {
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Error al crear el socket");
        return false;
    }

    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr) <= 0) {
        perror("Dirección inválida");
        return false;
    }

    std::cout << "Conectando a " << ip << ":" << port << std::endl;
    if (connect(sockfd, reinterpret_cast<sockaddr *>(&serv_addr), sizeof(serv_addr)) < 0) {
        perror("Fallo en la conexión");
        return false;
    }

    std::cout << "Conexión establecida." << std::endl;
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
        std::cerr << "No se pudo enviar el comando 0x" << std::hex << static_cast<int>(cmd) << std::dec << std::endl;
    }
}

void set_sample_rate(int sockfd, uint32_t sample_rate) {
    send_command(sockfd, 0x02, sample_rate);
    std::cout << "Tasa de muestreo establecida a " << sample_rate << " Hz" << std::endl;
}

void set_center_freq(int sockfd, uint32_t freq) {
    send_command(sockfd, 0x01, freq);
    std::cout << "Frecuencia central establecida a " << freq << " Hz" << std::endl;
}

void set_gain_mode(int sockfd, uint8_t mode) {
    send_command(sockfd, 0x03, mode);
    std::cout << "Modo de ganancia establecido a " << (mode == 0 ? "automático" : "manual") << std::endl;
}

void set_gain(int sockfd, uint32_t gain) {
    send_command(sockfd, 0x04, gain);
    std::cout << "Ganancia del sintonizador establecida a " << gain / 10.0 << " dB" << std::endl;
}

void set_agc_mode(int sockfd, uint8_t mode) {
    send_command(sockfd, 0x06, mode);
    std::cout << "AGC del sintonizador establecido a " << (mode == 0 ? "desactivado" : "activado") << std::endl;
}

void set_rtl_agc_mode(int sockfd, uint8_t mode) {
    send_command(sockfd, 0x0A, mode);
    std::cout << "RTL AGC establecido a " << (mode == 0 ? "desactivado" : "activado") << std::endl;
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
}

void apply_squelch(std::vector<float> &audio_samples, float squelch_level) {
    // Aplicar squelch a los datos de audio
    for (auto &sample : audio_samples) {
        if (std::abs(sample) < squelch_level) {
            sample = 0.0f;
        }
    }
}

void apply_de_emphasis(std::vector<float> &audio_samples, float sample_rate) {
    // Aplicar filtro de de-énfasis
    float RC = DE_EMPHASIS_TIME_CONSTANT;
    float dt = 1.0f / sample_rate;
    float alpha = dt / (RC + dt);

    float previous_output = 0.0f;
    for (auto &sample : audio_samples) {
        float output = alpha * sample + (1.0f - alpha) * previous_output;
        previous_output = output;
        sample = output;
    }
}

void resample_audio(const std::vector<float> &input_samples, std::vector<float> &output_samples, float input_rate, float output_rate) {
    float resample_ratio = output_rate / input_rate;
    size_t output_size = static_cast<size_t>(input_samples.size() * resample_ratio);
    output_samples.resize(output_size);

    for (size_t i = 0; i < output_size; ++i) {
        float t = i / resample_ratio;
        size_t idx = static_cast<size_t>(t);
        if (idx + 1 < input_samples.size()) {
            float frac = t - idx;
            output_samples[i] = input_samples[idx] * (1.0f - frac) + input_samples[idx + 1] * frac;
        } else {
            output_samples[i] = input_samples.back();
        }
    }
}

void write_wav_file(const std::string &filename, const std::vector<float> &audio_data, int sample_rate) {
    // Normalizar datos de audio
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

    // Configurar parámetros del archivo WAV
    SF_INFO sf_info{};
    sf_info.samplerate = sample_rate;
    sf_info.channels = 1;
    sf_info.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;

    SNDFILE *outfile = sf_open(filename.c_str(), SFM_WRITE, &sf_info);
    if (!outfile) {
        std::cerr << "Error al abrir el archivo de salida: " << sf_strerror(nullptr) << std::endl;
        return;
    }

    sf_count_t frames_written = sf_write_short(outfile, audio_int16.data(), audio_int16.size());
    if (frames_written != static_cast<sf_count_t>(audio_int16.size())) {
        std::cerr << "Error al escribir datos de audio en el archivo." << std::endl;
    }

    sf_close(outfile);
}
