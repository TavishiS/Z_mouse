import torch
import librosa
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import numpy as np
import certainty

# Load pretrained model
MODEL_PATH = "superb/wav2vec2-base-superb-er"
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_PATH)
model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=7, ignore_mismatched_sizes=True)
model.eval()

# Initial model emotion classes
model_emotions = {
    0: 'sad', 1: 'neutral', 2: 'angry', 3: 'happy',
    4: 'fear', 5: 'surprise', 6: 'disgust'
}

# Valence-arousal mapping for model emotions
va_map = {
    "sad": (0.2, 0.3), "neutral": (0.5, 0.5), "angry": (0.1, 0.9),
    "happy": (0.9, 0.8), "fear": (0.1, 0.85), "surprise": (0.7, 0.9),
    "disgust": (0.2, 0.6)
}

# Expanded Circumplex emotion labels with valence-arousal
circumplex_emotions = {
    "relaxed": (0.7, 0.2), "calm": (0.6, 0.3), "bored": (0.3, 0.2),
    "tired": (0.2, 0.2), "content": (0.7, 0.4), "excited": (0.95, 0.95),
    "alert": (0.8, 0.85), "tense": (0.2, 0.8), "nervous": (0.3, 0.9),
    "stressed": (0.3, 0.85), "serene": (0.8, 0.3), "depressed": (0.1, 0.2)
}

def preprocess_audio(audio_file):
    """Load and normalize audio"""
    speech, sr = librosa.load(audio_file, sr=16000)
    speech = librosa.util.normalize(speech)
    return speech

def closest_circumplex_emotion(valence, arousal):
    """Find closest matching emotion in circumplex space"""
    min_dist = float('inf')
    best_emotion = None
    for emotion, (v, a) in circumplex_emotions.items():
        dist = np.sqrt((valence - v) ** 2 + (arousal - a) ** 2)
        if dist < min_dist:
            min_dist = dist
            best_emotion = emotion
    return best_emotion

def predict_expanded_emotion(audio_file):
    """Predict and expand emotion using circumplex model"""
    speech = preprocess_audio(audio_file)
    inputs = feature_extractor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_idx = torch.argmax(logits, dim=-1).item()
    base_emotion = model_emotions.get(predicted_idx, "unknown")

    valence, arousal = va_map.get(base_emotion, (0.5, 0.5))
    expanded_emotion = closest_circumplex_emotion(valence, arousal)

    return {
        "model_emotion": base_emotion,
        "valence": valence,
        "arousal": arousal,
        "circumplex_emotion": expanded_emotion
    }

# Example
if __name__ == "__main__":
    audio_path = "fear.mp3"
    result = predict_expanded_emotion(audio_path)
    print(f"Model Emotion: {result['model_emotion']}")
    print(f"Valence: {result['valence']}, Arousal: {result['arousal']}")
    print(f"Circumplex Emotion: {result['circumplex_emotion']}")
    valence_circumplex, arousal_circumplex = circumplex_emotions[result['circumplex_emotion']]
    print(f"Valence_circumplex: {valence_circumplex}, Arousal_circumplex: {arousal_circumplex}")

    valence_label, valence_strength=certainty.fuzzy_label(valence_circumplex, certainty.x_valence, certainty.valence_low, certainty.valence_med, certainty.valence_high)
    arousal_label, arousal_strength=certainty.fuzzy_label(arousal_circumplex, certainty.x_arousal, certainty.arousal_low, certainty.arousal_med, certainty.arousal_high)

    print(f"Fuzzy Valence_circumplex: {valence_label} with a membership of ({valence_strength:.2f})")
    print(f"Fuzzy Arousal_circumplex: {arousal_label} with a membership of ({arousal_strength:.2f})")
