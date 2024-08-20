from faster_whisper import WhisperModel
import torch
import numpy as np
import os

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
        return transcript, self.transcript_score(log_probs)

    
    def transcript_score(self, log_probs):
        log_probs = np.array(log_probs)
        log_probs = (log_probs - self.min_log_prob) / (self.max_log_prob - self.min_log_prob)
        return log_probs.mean()
    