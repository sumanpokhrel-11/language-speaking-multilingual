#!/usr/bin/env python3

"""
Seamless English Speaking Practice Script
Natural conversation flow without interrupting prompts
"""

import ollama
import time
from datetime import datetime

# Try to import speech libraries
try:
    import speech_recognition as sr
    import pyttsx3
    SPEECH_AVAILABLE = True
    print("🔊 Speech features available!")
except ImportError:
    SPEECH_AVAILABLE = False
    print("📝 Speech libraries not installed. Please install: pip3 install speechrecognition pyttsx3 pyaudio")

class SeamlessSpokenEnglishBot:
    def __init__(self, model_name="llama3.2:3b"):
        self.model_name = model_name
        self.conversation_history = []
        self.session_start = datetime.now()
        self.speaking_time = 0
        self.auto_speak = True
        self.use_online_tts = False  # Will be set during voice selection
        
        # Initialize speech components if available
        if SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.tts_engine = pyttsx3.init()
            self.microphone = sr.Microphone()
            
            # Check for high-quality English voices
            self.setup_voice_selection()
            
            # Optimize speech settings
            rate = self.tts_engine.getProperty('rate')
            self.tts_engine.setProperty('rate', 160)  # Natural pace
            
            volume = self.tts_engine.getProperty('volume')
            self.tts_engine.setProperty('volume', 0.9)
        
        # Practice topics for seamless conversation
        self.practice_topics = {
            "beginner": {
                "personal": [
                    "Tell me about yourself and where you're from",
                    "What do you do for work or study?",
                    "Describe your family to me",
                    "What are your favorite hobbies?",
                    "Tell me about a typical day in your life"
                ],
                "situations": [
                    "You're at a restaurant ordering food. Show me how you'd order your favorite meal",
                    "You need directions to the nearest bank. Ask me for help",
                    "You're meeting a new coworker. Introduce yourself",
                    "You're shopping for clothes. Ask about sizes and prices",
                    "You want to invite a friend for coffee. Make the invitation"
                ]
            },
            "intermediate": [
                "Tell me about a memorable trip you took",
                "Describe a challenge you faced and how you solved it",
                "What's a skill you'd like to learn and why?",
                "Tell me about someone who has influenced your life",
                "Describe your ideal weekend",
                "What's your opinion on working from home?",
                "How has technology changed your daily life?",
                "What's the best advice you've ever received?"
            ],
            "advanced": [
                "What's your perspective on social media's impact on society?",
                "How do you think education will change in the next 10 years?",
                "Discuss the balance between work and personal life",
                "What role should governments play in environmental protection?",
                "How can we address inequality in society?",
                "What would you do if you were the leader of your country for a day?",
                "Discuss the advantages and disadvantages of globalization",
                "How might artificial intelligence change our future?"
            ]
        }
        
    def listen_for_command(self, prompt_text):
        """Listen for voice commands like 'next', 'repeat', 'enter'"""
        if not SPEECH_AVAILABLE:
            return input(prompt_text)
        
        print(f"🎤 {prompt_text}")
        print("💬 Say: 'next', 'repeat', or 'enter'")
        
        try:
            with self.microphone as source:
                print("🎤 Listening for command... (or wait for speech to finish)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=20, phrase_time_limit=5)
            
            # Stop any ongoing speech when command is detected
            self.stop_speaking()
            
            command = self.recognizer.recognize_google(audio, language='en-US').lower()
            print(f"👤 Command: '{command}'")
            
            if any(word in command for word in ['next', 'continue', 'go', 'skip']):
                return 'next'
            elif any(word in command for word in ['repeat', 'again', 'retry', 'redo']):
                return 'repeat'  
            elif any(word in command for word in ['enter', 'okay', 'yes', 'ready']):
                return 'enter'
            else:
                print(f"💡 I heard '{command}' - treating as 'enter'")
                return 'enter'
                
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            print("❌ Didn't catch that. Using 'enter' as default.")
            return 'enter'

    def check_ollama_connection(self):
        """Check Ollama connection"""
        try:
            models_response = ollama.list()
            available_models = []
            
            if hasattr(models_response, 'models'):
                for model in models_response.models:
                    if hasattr(model, 'model'):
                        available_models.append(model.model)
            
            return self.model_name in available_models
        except Exception as e:
            print(f"❌ Ollama connection failed: {str(e)}")
            return False

    def setup_voice_selection(self):
        """Setup native English voice selection"""
        voices = self.tts_engine.getProperty('voices')
        
        # Filter for native English voices
        english_voices = []
        
        # Look for high-quality English voices
        native_keywords = [
            'english', 'en-us', 'en-gb', 'en-au',  # Language codes
            'american', 'british', 'australian',   # Accents
            'hazel', 'karen', 'daniel', 'samantha', # macOS voices
            'david', 'zira', 'mark', 'susan',      # Windows voices
            'native', 'natural', 'premium'         # Quality indicators
        ]
        
        for voice in voices:
            voice_info = f"{voice.name} {voice.id}".lower()
            if any(keyword in voice_info for keyword in native_keywords):
                english_voices.append(voice)
        
        if not english_voices:
            english_voices = voices[:5]  # Fallback to first 5 voices
        
        print(f"\n🎤 Voice Selection for English Practice")
        print("=" * 40)
        print("🌍 Choose a native English accent:")
        
        # Categorize voices by accent if possible
        us_voices = [v for v in english_voices if any(kw in f"{v.name} {v.id}".lower() 
                     for kw in ['us', 'american', 'zira', 'david', 'hazel'])]
        uk_voices = [v for v in english_voices if any(kw in f"{v.name} {v.id}".lower() 
                     for kw in ['gb', 'british', 'uk', 'daniel', 'kate'])]
        au_voices = [v for v in english_voices if any(kw in f"{v.name} {v.id}".lower() 
                     for kw in ['au', 'australian', 'karen', 'lee'])]
        
        voice_options = []
        option_num = 1
        
        if us_voices:
            print(f"\n🇺🇸 American English:")
            for voice in us_voices[:2]:  # Max 2 per accent
                print(f"   {option_num}. {voice.name}")
                voice_options.append(voice)
                option_num += 1
        
        if uk_voices:
            print(f"\n🇬🇧 British English:")
            for voice in uk_voices[:2]:
                print(f"   {option_num}. {voice.name}")
                voice_options.append(voice)
                option_num += 1
        
        if au_voices:
            print(f"\n🇦🇺 Australian English:")
            for voice in au_voices[:2]:
                print(f"   {option_num}. {voice.name}")
                voice_options.append(voice)
                option_num += 1
        
        # Add other good English voices
        other_voices = [v for v in english_voices if v not in us_voices + uk_voices + au_voices]
        if other_voices:
            print(f"\n🌐 Other English Voices:")
            for voice in other_voices[:2]:
                print(f"   {option_num}. {voice.name}")
                voice_options.append(voice)
                option_num += 1
        
        # Online TTS option
        print(f"\n🌐 Online High-Quality Option:")
        print(f"   {option_num}. Use Google Text-to-Speech (requires internet)")
        
        print(f"\n💡 Recommendation: Try option 1-3 for native accents")
        
        while True:
            choice = input(f"\nChoose voice (1-{option_num}) or press Enter for auto-select: ").strip()
            
            if choice == str(option_num):  # Online TTS choice
                self.use_online_tts = True
                print("✅ Will use Google Text-to-Speech (online)")
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(voice_options):
                selected_voice = voice_options[int(choice) - 1]
                self.tts_engine.setProperty('voice', selected_voice.id)
                print(f"✅ Selected: {selected_voice.name}")
                self.use_online_tts = False
                # Test the voice
                print("🧪 Testing voice...")
                self.speak_text("Hello! This is how I'll sound during our English practice.")
                break
            elif choice == "":
                # Auto-select best available voice
                if voice_options:
                    selected_voice = voice_options[0]
                    self.tts_engine.setProperty('voice', selected_voice.id)
                    print(f"✅ Auto-selected: {selected_voice.name}")
                    self.use_online_tts = False
                    print("🧪 Testing voice...")
                    self.speak_text("Hello! This is how I'll sound during our English practice.")
                break
            else:
                print("❌ Please choose a valid option")

    def speak_text(self, text):
        """Speak text using selected voice method"""
        if not SPEECH_AVAILABLE or not self.auto_speak:
            return
            
        if hasattr(self, 'use_online_tts') and self.use_online_tts:
            self.speak_with_google_tts(text)
        else:
            print("🔊 Speaking...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def stop_speaking(self):
        """Stop any ongoing speech"""
        if hasattr(self, 'use_online_tts') and self.use_online_tts:
            try:
                import pygame
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except:
                pass
        else:
            self.tts_engine.stop()

    def speak_with_google_tts(self, text):
        """Use Google TTS for higher quality voice"""
        try:
            import requests
            import io
            import pygame
            import threading
            
            # Google TTS API (free, no key required)
            print("🔊 Speaking with Google TTS...")
            
            # Split long text into chunks to avoid TTS limits
            chunks = self.split_text_for_tts(text)
            
            for chunk in chunks:
                # Prepare the request
                url = "https://translate.google.com/translate_tts"
                params = {
                    'ie': 'UTF-8',
                    'q': chunk,
                    'tl': 'en-us',  # US English
                    'client': 'tw-ob',
                    'ttsspeed': '0.7'  # Slower for learning
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Initialize pygame mixer for audio playback
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    
                    # Load and play the audio
                    audio_data = io.BytesIO(response.content)
                    pygame.mixer.music.load(audio_data)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                        
                else:
                    print("❌ Online TTS failed, using system voice")
                    self.tts_engine.say(chunk)
                    self.tts_engine.runAndWait()
                    
        except ImportError:
            print("❌ Online TTS requires: pip install requests pygame")
            print("🔄 Using system voice instead")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ Online TTS error: {str(e)}")
            print("🔄 Using system voice instead")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def split_text_for_tts(self, text, max_length=200):
        """Split long text into chunks for TTS"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def listen_for_speech(self, timeout=60):
        """Listen for speech input with better error handling"""
        if not SPEECH_AVAILABLE:
            return input("👤 Your response: ")
        
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self.microphone as source:
                    print("🎤 Listening... (speak clearly and take your time)")
                    # Longer adjustment for better recognition
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                    # Longer phrase time limit for complete thoughts
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=120)
                
                print("🔄 Processing your speech...")
                text = self.recognizer.recognize_google(audio, language='en-US')
                
                if len(text.split()) < 2:  # Very short responses
                    print(f"👤 I heard: '{text}' - but that seems quite short.")
                    continue_choice = input("Would you like to say more or continue? [say more/continue]: ").strip().lower()
                    if continue_choice.startswith('s'):  # "say more"
                        print("🎤 Please continue speaking...")
                        more_audio = self.recognizer.listen(source, timeout=60, phrase_time_limit=120)
                        more_text = self.recognizer.recognize_google(more_audio, language='en-US')
                        text = text + " " + more_text
                
                return text
                
            except sr.UnknownValueError:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"❌ Sorry, I couldn't understand that clearly. Let's try again ({retry_count}/{max_retries})")
                    print("💡 Tip: Speak clearly and make sure you're in a quiet environment")
                else:
                    print("❌ Having trouble with speech recognition. Let's try typing instead.")
                    return input("👤 Please type your response: ")
                    
            except sr.RequestError as e:
                print(f"❌ Speech service error: {str(e)}")
                return input("👤 Please type your response: ")
                
            except sr.WaitTimeoutError:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"⏰ No speech detected. Let's try again ({retry_count}/{max_retries})")
                    print("💡 Tip: Make sure to speak after you see 'Listening...'")
                else:
                    print("⏰ Let's try typing instead.")
                    return input("👤 Please type your response: ")
        
        return input("👤 Please type your response: ")

    def get_ai_feedback(self, user_response, question, difficulty):
        """Get comprehensive AI feedback"""
        system_prompt = f"""You are an encouraging English conversation tutor. The student just answered: "{question}"

Their response was: "{user_response}"

Level: {difficulty}

Provide feedback that includes:
1. Positive encouragement about what they did well
2. Gentle corrections for any errors (grammar, vocabulary, pronunciation hints)
3. Suggestions to expand their answer or improve fluency
4. A natural follow-up question to continue the conversation

Keep feedback conversational, supportive, and specific. Focus on building confidence while improving their English."""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"My response was: '{user_response}'"}
                ]
            )
            
            if response and 'message' in response:
                return response['message']['content']
            else:
                return "Great job speaking English! Keep practicing."
                
        except Exception as e:
            return f"Good effort! Let's continue practicing. (Error: {str(e)})"

    def practice_conversation(self, difficulty, category=None):
        """Run seamless conversation practice"""
        
        # Get appropriate questions
        if difficulty == "beginner" and category:
            questions = self.practice_topics[difficulty][category]
            print(f"\n🗣️ Speaking Practice - Beginner {category.title()}")
        else:
            questions = self.practice_topics[difficulty]
            print(f"\n🗣️ Speaking Practice - {difficulty.title()} Level")
        
        print("=" * 50)
        print("🎤 Ready for natural conversation practice!")
        print("⏰ Speak naturally - I'll listen and give you feedback")
        print("💡 Say 'next question' or 'finish' to control the session\n")
        
        # Initial greeting and first question setup
        greeting = "Hi! I'm your English conversation partner. Let's practice speaking naturally. I'll ask you questions one by one, listen carefully to your answers, and give you helpful feedback."
        print(f"🤖 Tutor: {greeting}")
        self.speak_text(greeting)
        
        print(f"\n📋 Today we'll practice {len(questions)} questions about {difficulty} level topics.")
        setup_msg = f"I'll ask you {len(questions)} questions. Take your time with each answer - there's no rush!"
        print(f"🤖 Tutor: {setup_msg}")
        self.speak_text(setup_msg)
        
        input_command = self.listen_for_command("Press Enter when you're ready to start the first question...")
        
        question_count = 0
        
        for question in questions:
            question_count += 1
            print(f"\n" + "="*50)
            print(f"🎯 Question {question_count}/{len(questions)}")
            print(f"🤖 Tutor: {question}")
            
            # Always speak the question aloud
            print("🔊 Reading question aloud...")
            self.speak_text(question)
            
            print(f"\n💭 Take your time to think about your answer...")
            print("🎤 When you're ready, start speaking. I'll listen for up to 2 minutes.")
            print("💡 Try to speak for at least 30 seconds to practice fluency")
            
            # Get user response
            speaking_start = time.time()
            user_response = self.listen_for_speech()
            speaking_duration = time.time() - speaking_start
            self.speaking_time += speaking_duration
            
            if not user_response:
                continue
            
            # Check for control commands
            if user_response.lower() in ['next question', 'next', 'skip']:
                print("⏭️ Moving to next question...")
                continue
            elif user_response.lower() in ['finish', 'stop', 'quit', 'done']:
                print("🏁 Finishing practice session...")
                break
            elif user_response.lower() in ['repeat question', 'repeat', 'again']:
                print(f"🔄 Repeating: {question}")
                self.speak_text(question)
                continue
            
            # Display what user said clearly
            print(f"\n" + "="*50)
            print(f"👤 YOU SAID:")
            print(f"   \"{user_response}\"")
            print(f"⏱️ Speaking time: {speaking_duration:.1f} seconds")
            print(f"📝 Word count: {len(user_response.split())} words")
            print("="*50)
            
            # Get and display feedback
            print(f"\n🤖 Getting personalized feedback...")
            feedback = self.get_ai_feedback(user_response, question, difficulty)
            
            print(f"\n💬 TUTOR FEEDBACK:")
            print(f"{feedback}")
            print("\n🔊 Reading feedback aloud with Google TTS...")
            
            # Always speak feedback using the same voice (Google TTS)
            self.speak_text(feedback)
            
            # Wait for user to be ready for next question
            if question_count < len(questions):
                print(f"\n" + "="*50)
                print("✅ Feedback complete!")
                print("⏳ Processing feedback...")
                
                # Use voice commands with better flow control
                while True:
                    command = self.listen_for_command("What would you like to do?")
                    
                    if command == 'repeat':
                        print("🔄 Let's try this question again!")
                        print(f"🤖 Tutor: {question}")
                        print("🔊 Reading question again...")
                        self.speak_text(question)
                        
                        # Let them answer the same question again
                        print(f"\n💭 Take your time to think about your answer...")
                        print("🎤 When ready, give it another try!")
                        
                        # Get new response
                        speaking_start = time.time()
                        new_response = self.listen_for_speech()
                        new_speaking_duration = time.time() - speaking_start
                        
                        if new_response and not new_response.lower() in ['next question', 'next', 'skip', 'finish', 'stop', 'quit', 'done']:
                            print(f"\n" + "="*50)
                            print(f"👤 YOUR NEW ANSWER:")
                            print(f"   \"{new_response}\"")
                            print(f"⏱️ Speaking time: {new_speaking_duration:.1f} seconds")
                            print(f"📝 Word count: {len(new_response.split())} words")
                            print("="*50)
                            
                            # Get new feedback
                            print(f"\n🤖 Getting feedback on your new answer...")
                            new_feedback = self.get_ai_feedback(new_response, question, difficulty)
                            print(f"\n💬 NEW FEEDBACK:")
                            print(f"{new_feedback}")
                            print("\n🔊 Reading new feedback...")
                            self.speak_text(new_feedback)
                            
                            # Update conversation history
                            self.conversation_history.append({"role": "user", "content": new_response})
                            self.conversation_history.append({"role": "assistant", "content": new_feedback})
                            
                        print("\n✅ Ready for next question!")
                        input("Press Enter to continue...")
                        break
                        
                    elif command in ['next', 'enter']:
                        print(f"➡️ Moving to next question...")
                        time.sleep(1)
                        break
                    else:
                        print("💡 Say 'next' to continue or 'repeat' to try the question again")
                        continue
        
        self.show_practice_stats()

    def free_conversation(self):
        """Completely free conversation practice"""
        print("\n💬 Free Conversation Mode")
        print("=" * 40)
        
        greeting = "Let's have a free conversation! Talk about anything you want - your day, your thoughts, your dreams. I'm here to listen and help you practice English naturally."
        print(f"🤖 Tutor: {greeting}")
        self.speak_text(greeting)
        
        conversation_count = 0
        
        while True:
            conversation_count += 1
            print(f"\n🎤 Conversation turn {conversation_count}")
            print("🗣️ Say whatever comes to mind...")
            
            user_response = self.listen_for_speech(timeout=60)
            
            if not user_response or user_response.lower() in ['finish', 'stop', 'quit', 'done', 'goodbye']:
                print("👋 Thanks for the great conversation!")
                break
            
            print(f"\n👤 You said: \"{user_response}\"")
            
            # Get conversational response
            feedback = self.get_ai_feedback(user_response, "free conversation", "conversational")
            print(f"\n🤖 Tutor: {feedback}")
            self.speak_text(feedback)

    def pronunciation_drill(self):
        """Quick pronunciation practice"""
        print("\n🎯 Pronunciation Practice")
        print("=" * 40)
        
        # Common challenging sounds
        drills = [
            {"sound": "TH sounds", "words": ["think", "this", "thank", "mother", "weather"]},
            {"sound": "R and L", "words": ["red", "led", "right", "light", "really"]},
            {"sound": "V and W", "words": ["very", "worry", "voice", "choice", "review"]}
        ]
        
        intro = "Let's practice some challenging English sounds. I'll say a word, then you repeat it. Ready?"
        print(f"🤖 Tutor: {intro}")
        self.speak_text(intro)
        
        for drill in drills:
            print(f"\n🎯 Practicing: {drill['sound']}")
            sound_intro = f"Now let's practice {drill['sound']}. Listen and repeat each word."
            print(f"🤖 Tutor: {sound_intro}")
            self.speak_text(sound_intro)
            
            for word in drill['words']:
                print(f"\n🔊 Model word: {word}")
                self.speak_text(word)
                
                print(f"🎤 Now you say: {word}")
                user_pronunciation = self.listen_for_speech(timeout=10)
                
                if user_pronunciation:
                    print(f"👤 You said: \"{user_pronunciation}\"")
                    if word.lower() in user_pronunciation.lower():
                        feedback = "Perfect! Great pronunciation."
                    else:
                        feedback = f"Good try! Let's practice '{word}' again."
                    print(f"💬 {feedback}")
                    self.speak_text(feedback)

    def show_practice_stats(self):
        """Show practice session statistics"""
        duration = datetime.now() - self.session_start
        print(f"\n" + "="*50)
        print(f"📊 Practice Session Complete!")
        print(f"⏱️ Total session time: {str(duration).split('.')[0]}")
        if SPEECH_AVAILABLE and self.speaking_time > 0:
            print(f"🗣️ Your speaking time: {self.speaking_time:.1f} seconds")
            speaking_percentage = (self.speaking_time / duration.total_seconds()) * 100
            print(f"📈 Speaking percentage: {speaking_percentage:.1f}%")
        print(f"💪 Excellent work practicing your English speaking!")
        print("="*50)

    def settings_menu(self):
        """Quick settings adjustment"""
        print("\n⚙️ Settings")
        print("=" * 20)
        print(f"🔊 Auto-speak: {'ON' if self.auto_speak else 'OFF'}")
        
        if SPEECH_AVAILABLE:
            toggle = input("Toggle auto-speak? [y/N]: ").strip().lower()
            if toggle == 'y':
                self.auto_speak = not self.auto_speak
                print(f"🔊 Auto-speak is now {'ON' if self.auto_speak else 'OFF'}")

    def main_menu(self):
        """Streamlined main menu"""
        print("🗣️ English Speaking Practice")
        print("=" * 40)
        
        while True:
            print("\n📚 Practice Options:")
            print("  1. Beginner - Personal Topics")
            print("  2. Beginner - Everyday Situations") 
            print("  3. Intermediate Conversations")
            print("  4. Advanced Discussions")
            print("  5. Free Conversation")
            print("  6. Pronunciation Drills")
            print("  7. Settings")
            print("  8. Exit")
            
            choice = input("\nChoose (1-8): ").strip()
            
            if choice == "1":
                self.practice_conversation("beginner", "personal")
            elif choice == "2":
                self.practice_conversation("beginner", "situations")
            elif choice == "3":
                self.practice_conversation("intermediate")
            elif choice == "4":
                self.practice_conversation("advanced")
            elif choice == "5":
                self.free_conversation()
            elif choice == "6":
                self.pronunciation_drill()
            elif choice == "7":
                self.settings_menu()
            elif choice == "8":
                farewell = "Thanks for practicing English speaking with me! Keep up the great work!"
                print(f"🤖 {farewell}")
                self.speak_text(farewell)
                break
            else:
                print("❌ Please choose 1-8")

def main():
    """Main entry point"""
    if not SPEECH_AVAILABLE:
        print("❌ Speech features required for seamless practice")
        print("📦 Install with: pip3 install speechrecognition pyttsx3 pyaudio")
        return
    
    print("🔍 Checking Ollama connection...")
    
    bot = SeamlessSpokenEnglishBot()
    
    if not bot.check_ollama_connection():
        print("❌ Cannot connect to Ollama. Please start it with: ollama serve")
        return
    
    print("✅ Ready for seamless speaking practice!")
    
    # Welcome message
    welcome = "Welcome to seamless English speaking practice! I'll automatically speak questions and feedback, and show you exactly what I heard you say. Let's start!"
    print(f"\n🤖 {welcome}")
    bot.speak_text(welcome)
    
    bot.main_menu()

if __name__ == "__main__":
    main()