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


system_prompt = "Transcribe the following audio clip, where the clip is always in chilean spanish. If you can separate the \
	speakers, please do so. Please do not hallucinate or make up any information. If you are unsure about something, you can say so. If you need more context"


def generate_corrected_transcript(temperature, system_prompt, audio_file):
    response = model.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": transcribe_audio(audio_file)
            }
        ]
    )
    return completion.choices[0].message.content



def main():
	audio = "clip2.wav"
	corrected_text = generate_corrected_transcript(0, system_prompt, audio)
	print(corrected_text)

#Main
if __name__ == "__main__":
	main()
