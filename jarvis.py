import os
import sys
import time
import math
import queue
import threading
import subprocess
import shutil
import ctypes
import datetime
import webbrowser
import tkinter as tk
from tkinter import messagebox
from urllib.parse import quote

import customtkinter as ctk
import psutil
import pyautogui
import requests
import speech_recognition as sr
import pyttsx3


APP_NAME = "JARVIS"
BG = "#0a0f1c"
PANEL = "#101a2b"
PANEL2 = "#142239"
CYAN = "#00f0ff"
CYAN_DIM = "#087e91"
WHITE = "#e4f7ff"
MUTED = "#7895a8"

OLLAMA_URL = "http://localhost:11434"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


class Jarvis:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("J.A.R.V.I.S. | Desktop Intelligence")
        self.root.geometry("1100x760")
        self.root.minsize(850, 650)
        self.root.configure(fg_color=BG)

        self.running = True
        self.listening = threading.Event()
        self.speech_queue = queue.Queue()
        self.message_queue = queue.Queue()
        self.animation_phase = 0.0
        self.api_key = ""
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.api_model = "gpt-4o-mini"
        self.chat_history = []
        self._mic_error_reported = False

        self.build_ui()

        threading.Thread(target=self.tts_worker, daemon=True).start()
        threading.Thread(target=self.microphone_worker, daemon=True).start()

        self.root.after(50, self.process_messages)
        self.root.after(30, self.animate_reactor)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.log("JARVIS SYSTEM INITIALIZED")
        self.log("NEURAL INTERFACE ONLINE")
        self.log("LOCAL COMMAND ENGINE READY")
        self.log("AWAITING YOUR COMMAND")
        self.speak("JARVIS online. All systems operational.")

    def build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.root, fg_color=PANEL, corner_radius=12)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="J.A.R.V.I.S.",
            font=("Segoe UI", 27, "bold"), text_color=CYAN
        ).grid(row=0, column=0, padx=22, pady=15)

        ctk.CTkLabel(
            header, text="PERSONAL ARTIFICIAL INTELLIGENCE SYSTEM",
            font=("Consolas", 11), text_color=MUTED
        ).grid(row=0, column=1, sticky="w")

        self.status_label = ctk.CTkLabel(
            header, text="● SYSTEM ONLINE",
            font=("Consolas", 12, "bold"), text_color=CYAN
        )
        self.status_label.grid(row=0, column=2, padx=22)

        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.grid(row=1, column=0, padx=18, pady=8, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(main, fg_color=PANEL, corner_radius=14)
        left.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(
            left, text="CORE REACTOR",
            font=("Consolas", 14, "bold"), text_color=CYAN
        ).pack(pady=(22, 5))

        self.reactor = tk.Canvas(
            left, width=280, height=280, bg=PANEL, highlightthickness=0
        )
        self.reactor.pack(pady=10)

        self.reactor_status = ctk.CTkLabel(
            left, text="NEURAL CORE STANDBY",
            font=("Consolas", 11), text_color=MUTED
        )
        self.reactor_status.pack(pady=8)

        self.mic_button = ctk.CTkButton(
            left, text="ENABLE MICROPHONE", height=42,
            fg_color="#063d4b", hover_color="#075b70",
            border_color=CYAN, border_width=1, command=self.toggle_mic
        )
        self.mic_button.pack(padx=20, pady=10, fill="x")

        ctk.CTkButton(
            left, text="SETTINGS", height=38,
            fg_color=PANEL2, hover_color="#1b3450",
            command=self.open_settings
        ).pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(
            left, text="SYSTEM MONITOR",
            font=("Consolas", 12, "bold"), text_color=CYAN
        ).pack(pady=(20, 8))

        self.stats_label = ctk.CTkLabel(
            left, text="CPU: --\nRAM: --\nBATTERY: --",
            justify="left", font=("Consolas", 12), text_color=WHITE
        )
        self.stats_label.pack(pady=8)

        right = ctk.CTkFrame(main, fg_color=PANEL, corner_radius=14)
        right.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right, text="COMMAND INTERFACE",
            font=("Consolas", 14, "bold"), text_color=CYAN
        ).grid(row=0, column=0, padx=18, pady=16, sticky="w")

        self.log_box = ctk.CTkTextbox(
            right, fg_color="#080e19", text_color="#a9f7ff",
            font=("Consolas", 12), corner_radius=10, wrap="word"
        )
        self.log_box.grid(row=1, column=0, padx=15, pady=8, sticky="nsew")
        self.log_box.configure(state="disabled")

        input_panel = ctk.CTkFrame(right, fg_color="transparent")
        input_panel.grid(row=2, column=0, padx=12, pady=12, sticky="ew")
        input_panel.grid_columnconfigure(0, weight=1)

        self.command_input = ctk.CTkEntry(
            input_panel, height=45,
            placeholder_text="Enter a command for JARVIS...",
            fg_color="#080e19", border_color=CYAN_DIM,
            text_color=WHITE, font=("Segoe UI", 13)
        )
        self.command_input.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.command_input.bind("<Return>", lambda event: self.send_command())

        ctk.CTkButton(
            input_panel, text="SEND", width=90, height=45,
            fg_color="#006c80", hover_color="#008ca5",
            command=self.send_command
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            self.root,
            text="JARVIS INTELLIGENCE ENGINE  |  LOCAL + CLOUD  |  WINDOWS",
            font=("Consolas", 10), text_color=MUTED
        ).grid(row=2, column=0, pady=12)

        self.update_stats()

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        def update():
            if not self.running:
                return
            self.log_box.configure(state="normal")
            self.log_box.insert("end", f"[{timestamp}] {message}\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        if threading.current_thread() is threading.main_thread():
            update()
        else:
            self.message_queue.put(("log", message))

    def process_messages(self):
        if not self.running:
            return
        try:
            while True:
                kind, content = self.message_queue.get_nowait()
                if kind == "log":
                    self.log(content)
                elif kind == "reply":
                    self.log("JARVIS: " + content)
                    self.speak(content)
                elif kind == "status":
                    self.status_label.configure(text=content)
                elif kind == "mic":
                    self.mic_button.configure(text=content)
                elif kind == "reactor":
                    self.reactor_status.configure(text=content)
                elif kind == "confirm_sleep":
                    self.confirm_sleep()
        except queue.Empty:
            pass
        self.root.after(50, self.process_messages)

    def animate_reactor(self):
        if not self.running:
            return

        self.animation_phase += 0.07
        canvas = self.reactor
        canvas.delete("all")
        cx, cy = 140, 140
        pulse = 1 + 0.06 * math.sin(self.animation_phase)

        for radius in (105, 88, 69):
            r = radius * pulse
            canvas.create_oval(
                cx-r, cy-r, cx+r, cy+r,
                outline="#07566b", width=2
            )

        start = (self.animation_phase * 30) % 360
        canvas.create_arc(
            35, 35, 245, 245, start=start, extent=250,
            style="arc", outline=CYAN, width=4
        )
        canvas.create_arc(
            53, 53, 227, 227, start=-start, extent=190,
            style="arc", outline="#00a8d4", width=3
        )
        canvas.create_oval(
            92, 92, 188, 188, fill="#06394b", outline=CYAN, width=3
        )
        canvas.create_text(
            cx, cy, text="J", fill=WHITE,
            font=("Segoe UI", 54, "bold")
        )

        for i in range(32):
            angle = math.radians(i * 11.25 + start)
            x1 = cx + math.cos(angle) * 115
            y1 = cy + math.sin(angle) * 115
            x2 = cx + math.cos(angle) * 124
            y2 = cy + math.sin(angle) * 124
            canvas.create_line(
                x1, y1, x2, y2,
                fill=CYAN if i % 4 == 0 else CYAN_DIM, width=2
            )

        self.root.after(30, self.animate_reactor)

    def update_stats(self):
        if not self.running:
            return
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            battery_text = f"{battery.percent}%" if battery else "N/A"
            self.stats_label.configure(
                text=f"CPU: {cpu}%\nRAM: {ram}%\nBATTERY: {battery_text}"
            )
        except Exception:
            pass
        self.root.after(2000, self.update_stats)

    def send_command(self):
        command = self.command_input.get().strip()
        if not command:
            return
        self.command_input.delete(0, "end")
        self.log("YOU: " + command)
        threading.Thread(
            target=self.handle_command, args=(command,), daemon=True
        ).start()

    def handle_command(self, command):
        text = command.lower().strip()
        try:
            response = self.execute_local_command(text)
            if response is not None:
                self.message_queue.put(("reply", response))
                return

            self.message_queue.put(("status", "● AI PROCESSING"))
            response = self.ask_ai(command)
            self.message_queue.put(("reply", response))
            self.message_queue.put(("status", "● SYSTEM ONLINE"))
        except Exception as error:
            self.message_queue.put(("reply", f"An error occurred: {error}"))
            self.message_queue.put(("status", "● SYSTEM ONLINE"))

    def execute_local_command(self, text):
        if "what time" in text or text == "time":
            return "The current time is " + datetime.datetime.now().strftime("%I:%M %p")

        if "what date" in text or "today's date" in text or text == "date":
            return datetime.datetime.now().strftime("Today is %A, %d %B %Y.")

        if any(term in text for term in ("cpu", "ram", "battery", "system status")):
            cpu = psutil.cpu_percent(interval=0.3)
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            battery_info = f"{battery.percent} percent" if battery else "not available"
            return (
                f"System report. CPU usage {cpu} percent. "
                f"Memory usage {ram} percent. Battery {battery_info}."
            )

        if "open chrome" in text or "open google chrome" in text:
            return self.open_application("chrome")
        if "open notepad" in text:
            return self.open_application("notepad")
        if "open calculator" in text:
            return self.open_application("calculator")
        if "open vscode" in text or "open visual studio code" in text:
            return self.open_application("vscode")
        if "open explorer" in text or "open file explorer" in text:
            return self.open_application("explorer")

        if text.startswith("search web for "):
            query = text[len("search web for "):].strip()
            if not query:
                return "Please provide a search query."
            webbrowser.open("https://www.google.com/search?q=" + quote(query))
            return "Opening your web search."

        if "take screenshot" in text or "capture screen" in text:
            filename = datetime.datetime.now().strftime(
                "JARVIS_Screenshot_%Y%m%d_%H%M%S.png"
            )
            pictures = os.path.join(os.path.expanduser("~"), "Pictures")
            os.makedirs(pictures, exist_ok=True)
            path = os.path.join(pictures, filename)
            pyautogui.screenshot().save(path)
            return f"Screenshot saved to {path}."

        if "volume up" in text or "increase volume" in text:
            for _ in range(5):
                pyautogui.press("volumeup")
            return "System volume increased."

        if "volume down" in text or "decrease volume" in text:
            for _ in range(5):
                pyautogui.press("volumedown")
            return "System volume decreased."

        if "mute volume" in text or text == "mute":
            pyautogui.press("volumemute")
            return "Volume mute toggled."

        if "unmute volume" in text or text == "unmute":
            pyautogui.press("volumemute")
            return "Volume mute toggled."

        if "lock computer" in text or "lock pc" in text:
            ctypes.windll.user32.LockWorkStation()
            return "Locking the workstation."

        if text in ("sleep computer", "put computer to sleep", "sleep pc"):
            self.message_queue.put(("confirm_sleep", ""))
            return "A Windows sleep confirmation will appear."

        if text in ("help", "show commands", "what can you do"):
            return (
                "I can open Chrome, Notepad, Calculator, VS Code and Explorer. "
                "I can control volume, capture screenshots, report CPU, RAM "
                "and battery, tell the time and date, lock the PC, and answer "
                "general questions through an AI model."
            )

        return None

    def open_application(self, app):
        try:
            if app == "notepad":
                subprocess.Popen(["notepad.exe"])
            elif app == "calculator":
                subprocess.Popen(["calc.exe"])
            elif app == "explorer":
                subprocess.Popen(["explorer.exe"])
            elif app == "chrome":
                candidates = [
                    shutil.which("chrome"),
                    os.path.join(
                        os.environ.get("PROGRAMFILES", ""), "Google",
                        "Chrome", "Application", "chrome.exe"
                    ),
                    os.path.join(
                        os.environ.get("PROGRAMFILES(X86)", ""), "Google",
                        "Chrome", "Application", "chrome.exe"
                    ),
                    os.path.join(
                        os.environ.get("LOCALAPPDATA", ""), "Google",
                        "Chrome", "Application", "chrome.exe"
                    )
                ]
                executable = next(
                    (path for path in candidates if path and os.path.isfile(path)),
                    None
                )
                if executable:
                    subprocess.Popen([executable])
                else:
                    webbrowser.open("https://www.google.com")
            elif app == "vscode":
                executable = shutil.which("code")
                if executable:
                    subprocess.Popen([executable])
                else:
                    return (
                        "Visual Studio Code was not found in PATH. "
                        "Install VS Code or add its command-line launcher to PATH."
                    )
            return f"Opening {app}."
        except OSError as error:
            return f"Could not open {app}: {error}"

    def ask_ai(self, prompt):
        try:
            response = requests.get(OLLAMA_URL + "/api/tags", timeout=1.5)
            if response.ok:
                models = [
                    model.get("name", "")
                    for model in response.json().get("models", [])
                ]
                selected_model = next(
                    (model for model in models if model.startswith("llama3")), None
                )
                if not selected_model:
                    selected_model = next(
                        (model for model in models if model.startswith("mistral")), None
                    )

                if selected_model:
                    result = requests.post(
                        OLLAMA_URL + "/api/generate",
                        json={
                            "model": selected_model,
                            "prompt": (
                                "You are JARVIS, a helpful Windows desktop assistant. "
                                "Be accurate, concise and polite.\n" + prompt
                            ),
                            "stream": False
                        },
                        timeout=120
                    )
                    result.raise_for_status()
                    return result.json().get(
                        "response", "I could not generate a response."
                    ).strip()
        except (requests.RequestException, ValueError, KeyError):
            pass

        if not self.api_key:
            return (
                "I cannot reach a local Ollama model, and no cloud API key "
                "has been configured. Open Settings to configure your "
                "OpenAI-compatible API endpoint and key."
            )

        try:
            messages = [{
                "role": "system",
                "content": (
                    "You are JARVIS, a futuristic Windows AI assistant. "
                    "Be useful, clear, concise and accurate. "
                    "Do not claim to have performed actions you did not perform."
                )
            }]
            messages.extend(self.chat_history[-8:])
            messages.append({"role": "user", "content": prompt})

            result = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.api_model,
                    "messages": messages,
                    "temperature": 0.7
                },
                timeout=90
            )
            result.raise_for_status()
            answer = result.json()["choices"][0]["message"]["content"]
            self.chat_history.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer}
            ])
            self.chat_history = self.chat_history[-16:]
            return answer.strip()
        except requests.RequestException as error:
            return f"Cloud AI connection failed: {error}"
        except (ValueError, KeyError, IndexError, TypeError):
            return "The AI service returned an unexpected response."

    def speak(self, text):
        if self.running:
            self.speech_queue.put(text)

    def tts_worker(self):
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 0.9)
        except Exception as error:
            self.message_queue.put(("log", f"TTS initialization failed: {error}"))

        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if text is None:
                break
            if engine is None:
                continue
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as error:
                self.message_queue.put(("log", f"Speech error: {error}"))

        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass

    def toggle_mic(self):
        if self.listening.is_set():
            self.listening.clear()
            self.mic_button.configure(text="ENABLE MICROPHONE")
            self.reactor_status.configure(text="NEURAL CORE STANDBY")
            self.log("MICROPHONE DISABLED")
        else:
            self.listening.set()
            self.mic_button.configure(text="DISABLE MICROPHONE")
            self.reactor_status.configure(text="VOICE RECOGNITION ACTIVE")
            self.log("MICROPHONE ENABLED")

    def microphone_worker(self):
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        while self.running:
            if not self.listening.wait(timeout=0.5):
                continue

            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    self.message_queue.put(("log", "Listening for voice input..."))

                    while self.running and self.listening.is_set():
                        try:
                            audio = recognizer.listen(
                                source, timeout=2, phrase_time_limit=8
                            )
                            recognized = recognizer.recognize_google(
                                audio, language="en-US"
                            )
                            if recognized.strip():
                                self.message_queue.put(("log", "VOICE: " + recognized))
                                threading.Thread(
                                    target=self.handle_command,
                                    args=(recognized,), daemon=True
                                ).start()
                        except sr.WaitTimeoutError:
                            continue
                        except sr.UnknownValueError:
                            continue
                        except sr.RequestError as error:
                            self.message_queue.put(
                                ("log", f"Speech recognition service error: {error}")
                            )
                            time.sleep(2)
            except (OSError, AttributeError) as error:
                self.message_queue.put(("log", f"Microphone unavailable: {error}"))
                self.message_queue.put(("log", "Use the text command box instead."))
                self.listening.clear()
                self.message_queue.put(("mic", "ENABLE MICROPHONE"))
                self.message_queue.put(("reactor", "NEURAL CORE STANDBY"))
                time.sleep(2)

    def open_settings(self):
        window = ctk.CTkToplevel(self.root)
        window.title("JARVIS Settings")
        window.geometry("520x520")
        window.configure(fg_color=BG)
        window.transient(self.root)
        window.grab_set()

        ctk.CTkLabel(
            window, text="NEURAL CONFIGURATION",
            font=("Consolas", 20, "bold"), text_color=CYAN
        ).pack(pady=22)

        ctk.CTkLabel(
            window, text="OpenAI-compatible API endpoint", text_color=WHITE
        ).pack(anchor="w", padx=28)

        url_entry = ctk.CTkEntry(window, width=455, height=40)
        url_entry.pack(padx=25, pady=8)
        url_entry.insert(0, self.api_url)

        ctk.CTkLabel(window, text="Model name", text_color=WHITE).pack(
            anchor="w", padx=28, pady=(12, 0)
        )
        model_entry = ctk.CTkEntry(window, width=455, height=40)
        model_entry.pack(padx=25, pady=8)
        model_entry.insert(0, self.api_model)

        ctk.CTkLabel(window, text="API key", text_color=WHITE).pack(
            anchor="w", padx=28, pady=(12, 0)
        )
        key_entry = ctk.CTkEntry(window, width=455, height=40, show="*")
        key_entry.pack(padx=25, pady=8)
        key_entry.insert(0, self.api_key)

        ctk.CTkLabel(
            window,
            text=(
                "Leave the API key empty to use local Ollama only.\n"
                "Credentials are held in memory and are not saved to disk."
            ),
            text_color=MUTED, font=("Segoe UI", 11), justify="left"
        ).pack(pady=15)

        def save_settings():
            url = url_entry.get().strip()
            model = model_entry.get().strip()
            key = key_entry.get().strip()

            if not url.startswith(("https://", "http://")):
                messagebox.showerror(
                    "JARVIS Settings",
                    "Enter a valid HTTP or HTTPS API endpoint.",
                    parent=window
                )
                return
            if not model:
                messagebox.showerror(
                    "JARVIS Settings", "Model name cannot be empty.", parent=window
                )
                return

            self.api_url = url
            self.api_model = model
            self.api_key = key
            self.log("AI CONFIGURATION UPDATED")
            window.destroy()

        ctk.CTkButton(
            window, text="SAVE CONFIGURATION", height=45,
            fg_color="#006c80", hover_color="#008ca5",
            command=save_settings
        ).pack(padx=25, pady=12, fill="x")

    def confirm_sleep(self):
        if not self.running:
            return
        if messagebox.askyesno(
            "JARVIS", "Put Windows into sleep mode?", parent=self.root
        ):
            try:
                result = ctypes.windll.powrprof.SetSuspendState(False, False, False)
                if result:
                    self.log("Windows sleep request completed.")
                else:
                    self.log("Windows could not enter sleep mode.")
            except OSError as error:
                self.log(f"Sleep command failed: {error}")
        else:
            self.log("Sleep request cancelled.")

    def close(self):
        self.running = False
        self.listening.clear()
        self.speech_queue.put(None)
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if sys.platform != "win32":
        print("JARVIS is designed for Windows 10 and Windows 11.")
        sys.exit(1)

    app = Jarvis()
    app.run()
