import sounddevice as sd
import queue

class AudioInput:
    def __init__(self, device=None, channels=1, samplerate=44100, blocksize=1024, max_duration=60):
        self.device = device
        self.channels = channels
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.max_blocks = int((samplerate * max_duration) / blocksize)  # Max number of blocks for 1 minute
        self.q = queue.Queue(maxsize=self.max_blocks)  # Limited to 1 minute of audio
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Status: {status}")
        
        # Ensure we maintain only 1 minute of audio in the queue
        if self.q.full():
            try:
                self.q.get_nowait()  # Remove oldest block if the queue is full
            except queue.Empty:
                pass  # Shouldn't happen but handle just in case
        
        self.q.put(indata.copy())  # Add the new block

    def start_stream(self):
        self.stream = sd.InputStream(
            device=self.device,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._audio_callback
        )
        self.stream.start()

    def read_block(self):
        """Get the next audio block from the queue."""
        return self.q.get()

    def stop_stream(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()

    def is_active(self):
        """Check if the stream is active."""
        return self.stream.active if self.stream is not None else False

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    def update_plot(frame, audio_input, line):
        try:
            block = audio_input.read_block()
            line.set_ydata(np.concatenate((line.get_ydata()[len(block):], block.flatten())))
        except queue.Empty:
            pass
        return line,

    audio_input = AudioInput(blocksize=1024*3)
    audio_input.start_stream()

    fig, ax = plt.subplots()
    x = np.arange(0, audio_input.blocksize * 10)
    y = np.zeros(audio_input.blocksize * 10)
    line, = ax.plot(x, y)

    ax.set_ylim(-1, 1)
    ax.set_xlim(0, len(y))
    plt.ylabel('Amplitude')
    plt.xlabel('Samples')

    ani = FuncAnimation(fig, update_plot, fargs=(audio_input, line), interval=50, blit=True)
    plt.show()

    audio_input.stop_stream()