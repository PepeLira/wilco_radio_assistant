from openai import OpenAI
model = OpenAI()


def transcribe_audio(audio):
	audio_file = open(audio, "rb")
	transcription = model.audio.transcriptions.create(
		model='whisper-1',
		file=audio_file,
		prompt="Transcribe the following audio clip, where the clip is always in chilean spanish. If you can separate the speakers, please do so.",
	)

	return transcription.text






def main():
	audio = "clip2.wav"
	transcription = transcribe_audio(audio)
	print("Transcription:")
	print(transcription)

#Main
if __name__ == "__main__":
	main()
