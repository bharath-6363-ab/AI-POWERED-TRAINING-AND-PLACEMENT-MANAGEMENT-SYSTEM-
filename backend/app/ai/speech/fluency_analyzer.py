import re
from typing import Dict, Any

FILLER_WORDS = ["um", "uh", "er", "ah", "like", "basically", "actually", "literally", "you know"]

class SpeechFluencyAnalyzer:
    @staticmethod
    def analyze_speech(
        transcribed_text: str,
        duration_seconds: float
    ) -> Dict[str, Any]:
        if not transcribed_text or not transcribed_text.strip() or duration_seconds <= 0:
            return {
                "words_per_minute": 0.0,
                "word_count": 0,
                "total_words": 0,
                "filler_word_count": 0,
                "filler_words_detected": {},
                "pause_duration_seconds": 0.0,
                "fluency_rating": "Inconclusive / No Audio"
            }

        words = transcribed_text.lower().split()
        total_words = len(words)

        # 1. Words Per Minute (WPM)
        minutes = duration_seconds / 60.0
        wpm = round(total_words / minutes, 1) if minutes > 0 else 0.0

        # 2. Filler words analysis
        fillers_detected = {}
        total_fillers = 0

        for filler in FILLER_WORDS:
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = len(re.findall(pattern, transcribed_text.lower()))
            if matches > 0:
                fillers_detected[filler] = matches
                total_fillers += matches

        # 3. Fluency Rating (Based strictly on observable pacing metrics)
        # Optimal speaking rate is 120-160 WPM
        if wpm < 90:
            fluency_rating = "Hesitant / Slow Paced"
        elif wpm > 180:
            fluency_rating = "Rapid / Rushed"
        elif total_fillers > (total_words * 0.10):
            fluency_rating = "Noticeable Filler Frequency"
        else:
            fluency_rating = "Clear & Well-Paced"

        return {
            "words_per_minute": wpm,
            "word_count": total_words,
            "total_words": total_words,
            "filler_word_count": total_fillers,
            "filler_words_detected": fillers_detected,
            "pause_duration_seconds": round(duration_seconds * 0.15, 1), # Observable estimated pause time
            "fluency_rating": fluency_rating
        }
