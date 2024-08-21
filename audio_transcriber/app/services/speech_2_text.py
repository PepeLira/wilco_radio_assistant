from faster_whisper import WhisperModel
import torch
import numpy as np
import os
import datetime

class Speech2Text:
    def __init__(self, model_size=None, language="es"):
        os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
        self.model_size = "large-v3" if model_size is None else model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
        self.language = language
        self.min_log_prob = -1.62
        self.max_log_prob = -0.12 # max prob - min prob must be greater than 0
        self.clips_path = "./clips"

    def transcribe_clip(self, clip_path):
        segments, _ = self.model.transcribe(clip_path, beam_size=5, language=self.language)
        transcripts = []
        log_probs = []
        for segment in segments:
            if segment.text not in transcripts:
                transcripts.append(segment.text)
                log_probs.append(segment.avg_logprob)

        transcript = " ".join(transcripts)
        score = self.transcript_score(log_probs)
        parsed_data = self.parse_clip_data(clip_path, transcript, score)
        return parsed_data
    
    def transcript_score(self, log_probs):
        log_probs = np.array(log_probs)
        log_probs = (log_probs - self.min_log_prob) / (self.max_log_prob - self.min_log_prob)
        return log_probs.mean()
    
    def parse_clip_data(self, file_name, transcription, score):
        # input: file name is clip_{%Y%m%d_%H%M%S}_{clip_length_in_seconds}.wav
        # output: dict with date, time_start, time_end, duration "transcription", "summary", "date", "time_start", "time_end", "duration", "description", "score", "file_path".
        
        # Extract date, time_start, time_end, duration from file_name
        date, time_start, duration = file_name.split("_")[1:]
        time_start = time_start[:2] + ":" + time_start[2:4] + ":" + time_start[4:]
        time_start_datetime = datetime.datetime.strptime(time_start, "%H:%M:%S")
        duration = float(duration.split(".")[0])
        duration_datetime = datetime.timedelta(seconds=duration)
        time_end = (time_start_datetime + duration_datetime).strftime("%H:%M:%S")
        date = date[:4] + "/" + date[4:6] + "/" + date[6:]
        return {
            "transcription": transcription,
            "summary": '',
            "date": date,
            "time_start": time_start,
            "time_end": time_end,
            "duration": duration,
            "description": "Transcription of an audio clip.",
            "score": score,
            "file_path": file_name
        }

