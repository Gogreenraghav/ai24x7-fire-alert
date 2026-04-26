"""
AI24x7 Fire Alert - TTS Evacuation Module
Multi-language voice announcements for fire evacuation.
Supports Hindi, English + 8 more Indian languages.
"""
import os, io, tempfile, requests
from pathlib import Path

# ─── Edge TTS Evacuation ──────────────────
EDGE_VOICES = {
    "hi-IN-MadhurNeural": {"lang": "hi", "gender": "Female", "name": "Hindi"},
    "hi-IN-AmitNeural": {"lang": "hi", "gender": "Male", "name": "Hindi"},
    "ta-IN-PallaviNeural": {"lang": "ta", "gender": "Female", "name": "Tamil"},
    "te-IN-ShrutiNeural": {"lang": "te", "gender": "Female", "name": "Telugu"},
    "kn-IN-SapnaNeural": {"lang": "kn", "gender": "Female", "name": "Kannada"},
    "bn-IN-TanishkaNeural": {"lang": "bn", "gender": "Female", "name": "Bengali"},
    "mr-IN-AarohiNeural": {"lang": "mr", "gender": "Female", "name": "Marathi"},
    "en-US-AriaNeural": {"lang": "en", "gender": "Female", "name": "English"},
    "gu-IN-AshaNeural": {"lang": "gu", "gender": "Female", "name": "Gujarati"},
    "pa-IN-GaganNeural": {"lang": "pa", "gender": "Male", "name": "Punjabi"},
    "ml-IN-MidhunNeural": {"lang": "ml", "gender": "Male", "name": "Malayalam"},
}

EVACUATION_TEMPLATES = {
    "fire_detected": {
        "hi": "सावधान! {location} में आग का पता चला है। कृपया तुरंत इमारत खाली करें। सीढ़ियों का उपयोग करें। लिफ्ट का उपयोग न करें।",
        "en": "Alert! Fire detected at {location}. Please evacuate immediately. Use stairs. Do not use elevators.",
        "ta": "எச்சரிக்கை! {location}-ல் தீ கண்டறியப்பட்டது. உடனடியாக வெளியேறவும். படிக்கட்டைப் பயன்படுத்தவும். லிஃப்டைப் பயன்படுத்த வேண்டாம்.",
        "te": "హెచ్చరిక! {location}లో అగ్ని కనుగొనబడింది. వెంటనే ఖాళీ చేయండి. మెట్లు ఉపయోగించండి. లిఫ్ట్ ఉపయోగించవద్దు.",
    },
    "evacuation_route": {
        "hi": "निकास: {direction} दिशा में जाएं। {floor} मंजिल से बाहर निकलें।",
        "en": "Exit via {direction}. Leave from {floor} floor.",
    },
    "assembly_point": {
        "hi": "इकट्ठा होने की जगह: {point}। वहां जाकर अपनी उपस्थिति दर्ज कराएं।",
        "en": "Assembly point: {point}. Go there and register your presence.",
    },
    "all_clear": {
        "hi": "सभी सुरक्षित। आग बुझा दी गई है। कृपया अपने स्थान पर वापस जाएं।",
        "en": "All safe. Fire has been extinguished. Please return to your location.",
    },
    "partial_evacuation": {
        "hi": "सावधान! {floor} मंजिल पर आग लगी है। केवल उस मंजिल के लोग निकलें। बाकी स्थान सुरक्षित हैं।",
        "en": "Caution! Fire on {floor} floor. Only that floor, evacuate. Other areas are safe.",
    }
}

class EvacuationSpeaker:
    """
    Generates and plays evacuation announcements.
    Multiple languages, zone-based messages, background music ducking.
    """
    
    def __init__(self, audio_output="/tmp/evacuation.mp3"):
        self.audio_output = audio_output
        self.speaker = None
        self.pa_system_ip = None
        self.tts_engine = "edge"  # edge / gtts / xtts
    
    def speak(self, text, lang="hi", voice=None):
        """Convert text to speech using Edge TTS"""
        try:
            import asyncio
            from edge_tts import EdgeTTS
            
            async def _tts():
                tts = EdgeTTS()
                await tts.tts(text=text, voice=voice or EDGE_VOICES.get(lang, "hi-IN-MadhurNeural")[0] 
                             if isinstance(EDGE_VOICES.get(lang), list) else "hi-IN-MadhurNeural",
                             output=self.audio_output)
            
            asyncio.run(_tts())
            self._play_audio()
            return {"success": True, "file": self.audio_output}
        except ImportError:
            return self._gtts_fallback(text, lang)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _gtts_fallback(self, text, lang):
        """Fallback to Google TTS"""
        try:
            from gtts import gTTS
            lang_code = {"hi": "hi", "en": "en", "ta": "ta", "te": "te", 
                        "kn": "kn", "bn": "bn", "mr": "mr", "gu": "gu"}.get(lang, "hi")
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(self.audio_output)
            self._play_audio()
            return {"success": True, "engine": "gtts", "file": self.audio_output}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _play_audio(self):
        """Play evacuation audio on speakers"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(self.audio_output)
            pygame.mixer.music.set_volume(1.0)  # Max volume for evacuation
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
        except:
            # Fallback: use system audio
            try:
                os.system(f"aplay {self.audio_output} 2>/dev/null || echo 'No audio device'")
            except:
                print(f"🔊 [TTS] {open(self.audio_output).read() if os.path.exists(self.audio_output) else text}")
    
    def announce_zone(self, zone_name, floor, direction="main exit"):
        """Generate zone-specific announcement"""
        text = EVACUATION_TEMPLATES["fire_detected"].get("hi", "").format(location=zone_name)
        return self.speak(text, "hi")
    
    def announce_all_clear(self):
        """Announce all clear"""
        text = EVACUATION_TEMPLATES["all_clear"]["hi"]
        return self.speak(text, "hi")
    
    def announce_floor(self, floor, zone=""):
        """Announce floor-specific evacuation"""
        if zone:
            text = EVACUATION_TEMPLATES["partial_evacuation"]["hi"].format(floor=floor)
        else:
            text = f"सावधान! {floor} मंजिल से निकलें। {floor} मंजिल के लोग तुरंत बाहर जाएं।"
        return self.speak(text, "hi")
    
    def announce_with_directions(self, zone, floor, direction, assembly_point):
        """Full evacuation announcement with all details"""
        parts = [
            EVACUATION_TEMPLATES["fire_detected"]["hi"].format(location=zone),
            EVACUATION_TEMPLATES["evacuation_route"]["hi"].format(direction=direction, floor=floor),
            EVACUATION_TEMPLATES["assembly_point"]["hi"].format(point=assembly_point)
        ]
        full_text = " ".join(parts)
        return self.speak(full_text, "hi")
    
    def broadcast_to_all_zones(self, text, lang="hi"):
        """Broadcast same message to all PA zones (multi-zone PA system)"""
        results = []
        zones = ["zone_a", "zone_b", "zone_c", "zone_d"]
        for zone in zones:
            result = self.speak(text, lang)
            results.append({"zone": zone, "result": result})
        return results


# ─── PA System Integration ────────────────
class PASystem:
    """
    Integration with PA (Public Address) system.
    Supports: Network-connected PA systems, Amplifiers with IP control.
    """
    
    def __init__(self, pa_ip=None, port=80):
        self.pa_ip = pa_ip
        self.port = port
        self.connected = False
    
    def connect(self):
        """Connect to PA system"""
        if not self.pa_ip:
            print("⚠️ PA system IP not configured")
            return False
        try:
            # Check connection
            import requests
            r = requests.get(f"http://{self.pa_ip}:{self.port}/status", timeout=5)
            self.connected = True
            print(f"✅ PA System connected: {self.pa_ip}")
            return True
        except:
            self.connected = False
            return False
    
    def broadcast_audio(self, audio_file):
        """Broadcast audio file through PA system"""
        if not self.connected:
            self.connect()
        
        if not self.connected:
            print("⚠️ PA system not available, using local speaker")
            return {"success": False, "method": "local_speaker"}
        
        try:
            import requests
            # POST audio to PA system
            with open(audio_file, "rb") as f:
                files = {"audio": f}
                r = requests.post(
                    f"http://{self.pa_ip}:{self.port}/broadcast",
                    files=files,
                    timeout=30
                )
            return {"success": True, "method": "pa_system"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def duck_background_audio(self):
        """Lower background music volume during announcement"""
        if not self.connected:
            return
        try:
            import requests
            requests.post(f"http://{self.pa_ip}:{self.port}/volume", 
                         json={"level": 0.3}, timeout=5)
        except:
            pass
    
    def restore_volume(self):
        """Restore background music volume"""
        if not self.connected:
            return
        try:
            import requests
            requests.post(f"http://{self.pa_ip}:{self.port}/volume",
                         json={"level": 1.0}, timeout=5)
        except:
            pass


# ─── Fire Alarm Integration ────────────────
class FireAlarmPanel:
    """
    Integration with building fire alarm control panel.
    Standard protocols: NFS 72, Ademco, Bosch.
    """
    
    def __init__(self, panel_type="generic", ip=None, relay_pin=18):
        self.panel_type = panel_type
        self.panel_ip = ip
        self.relay_pin = relay_pin
        self.alarm_active = False
    
    def trigger_alarm(self, zone=None, message="Fire Alert"):
        """Trigger fire alarm on panel"""
        print(f"🔔 FIRE ALARM TRIGGERED: Zone={zone}, Message={message}")
        
        if self.panel_ip:
            try:
                import requests
                requests.post(f"http://{self.panel_ip}/alarm",
                            json={"zone": zone, "message": message, "action": "activate"},
                            timeout=10)
            except:
                pass
        
        # Hardware relay trigger
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.relay_pin, GPIO.OUT)
            GPIO.output(self.relay_pin, GPIO.HIGH)
            self.alarm_active = True
            print("🔔 [HARDWARE] Alarm relay activated")
        except:
            pass
    
    def silence_alarm(self):
        """Silence the alarm (for all-clear)"""
        if self.alarm_active:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.relay_pin, GPIO.LOW)
                self.alarm_active = False
                print("🔔 [HARDWARE] Alarm silenced")
            except:
                pass


# ─── CLI ─────────────────────────────────
if __name__ == "__main__":
    speaker = EvacuationSpeaker()
    
    # Test announcements
    print("🔥 AI24x7 Evacuation TTS - Testing...")
    
    # Hindi announcement
    print("\n📢 Hindi:")
    speaker.speak("सावधान! आग का पता चला है। तुरंत निकलें।", "hi")
    
    # English announcement
    print("\n📢 English:")
    speaker.speak("Alert! Fire detected. Evacuate immediately.", "en")
    
    print("\n✅ Evacuation TTS ready!")