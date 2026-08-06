import speech_recognition as sr
import sys
import asyncio
import tempfile
import os
import pygame
import edge_tts
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "app"))
from agents.supervisor import route_question

pygame.mixer.init()
VOICE = "en-US-JennyNeural"

async def _generate_speech(text: str, output_path: str):
    
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)
    
# Generates a temporary MP3, plays it via Pygame Mixer, and cleans up the temp file.
def speak_response(text: str): 

    print(f"\nNova: {text}")
    
    # Create temporary file to store audio stream
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        temp_path = fp.name

    try:
        # Run async TTS generation inside synchronous function wrapper
        asyncio.run(_generate_speech(text, temp_path))
        
        # Load and play synthesized speech stream
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"[Speech Synthesis Error] Fallback: {e}")
    finally:
        # Clean up temporary audio file from disk
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

 
def listen_and_transcribe():
    
    recognizer = sr.Recognizer() 
    recognizer.energy_threshold = 1000  
    recognizer.dynamic_energy_threshold = True 
    recognizer.pause_threshold = 1.8     
    recognizer.non_speaking_duration = 0.8 
    
    with sr.Microphone() as source:
        print("\n[Listening... Please speak into your microphone]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5) 
        audio = recognizer.listen(source)

    try:
        print("[Transcribing...]")
        # using Google for Listening (STT)
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        speak_response("Sorry, I didn't catch that. Could you please repeat?")
        return None
    except sr.RequestError:
        speak_response("My speech recognition service is currently unavailable.")
        return None

def start_voice_agent():
    """
    Main conversation loop maintaining session state, memory context, and voice turn-taking.
    chat_history is maintained here: Preserves multi-turn state across caller questions.
    """
    welcome_message = (
        "Hello! Welcome to Customer Support. I am Nova, your AI Voice Assistant. "
        "I can help you check order shipping status, cancel orders, update delivery addresses, "
        "report damaged items, or answer company policy questions. How can I assist you today?"
    )
    speak_response(welcome_message)
  

    chat_history = []
    
    while True:
        user_text = listen_and_transcribe()
        
        if user_text:
        
            if "goodbye" in user_text.lower() or "exit" in user_text.lower() or "bye" in user_text.lower():
                speak_response("Goodbye! Have a wonderful day.")
                break
                
            # 1. Invoke LangGraph Supervisor Workflow Graph
            answer = route_question(user_text, chat_history)
            
            # 2. Speak response cleanly through speakers
            speak_response(answer)
            
            # 3. Append conversation turn to short-term memory array
            chat_history.append({"role": "user", "content": user_text})
            chat_history.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    print("Starting Local Voice Agent with Microsoft Neural TTS (Jenny)...")
    start_voice_agent()
