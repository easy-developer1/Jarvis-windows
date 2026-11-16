# J.A.R.V.I.S. – Personal AI Desktop Assistant

**Your personal AI-powered Windows assistant.**

JARVIS is a futuristic desktop assistant built with Python, designed to bring voice interaction, AI conversations, and Windows automation together in one application.

Featuring a futuristic HUD-inspired interface, voice recognition, text-to-speech, local AI support, and Windows system controls.

---

## ✨ Features

- **Futuristic Interface:** Dark-themed HUD with cyan accents, animated reactor, and command console.
- **Voice Recognition:** Speak to JARVIS using your microphone.
- **Text-to-Speech:** JARVIS can respond with spoken voice.
- **AI Integration:** Connect to local AI models through Ollama or compatible cloud AI APIs.
- **Windows Automation:** Open applications and perform supported system actions.
- **System Monitoring:** View CPU, RAM, and battery information.
- **Quick Commands:** Check the time and date, take screenshots, search the web, and more.
- **Background Processing:** Voice recognition, speech generation, and AI requests run in background threads.

## 🖥️ Screenshots

Add screenshots of your JARVIS interface here.

## 🛠️ Technologies Used

- Python
- CustomTkinter
- PyAudio
- SpeechRecognition
- pyttsx3
- PyAutoGUI
- psutil
- Requests
- PyInstaller

## 📦 Installation

### 1. Download the project

Clone this repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Or download the repository as a ZIP file.

### 2. Open the project folder

```bash
cd JARVIS
```

### 3. Run the build script

Double-click:

```text
build_exe.bat
```

The script creates a virtual environment, installs the required dependencies, and builds the Windows executable.

### 4. Launch JARVIS

After successful compilation, find the executable here:

```text
dist/JARVIS.exe
```

## 🧠 AI Configuration

JARVIS supports two AI connection methods:

**Local AI – Ollama**
- Run an Ollama server on your computer.
- Download a compatible model.
- Make sure Ollama is accessible at `http://localhost:11434`.

**Cloud AI – OpenAI-Compatible API**
- Obtain an API key from a supported provider.
- Open JARVIS Settings.
- Enter the API endpoint, model name, and API key as required.

Cloud AI requires an internet connection. API providers may have separate usage limits and charges.

## 🎙️ Voice Features

JARVIS supports microphone-based speech recognition and spoken responses.

Speech recognition through the configured Google recognition service requires an internet connection.

## 🔒 Security

- API keys should remain private.
- Never upload API keys to GitHub.
- JARVIS uses predefined local commands rather than accepting arbitrary shell commands.
- Review the source code before running the application.

## 📁 Project Structure

```text
JARVIS/
│
├── jarvis.py
├── build_exe.bat
└── README.md
```

## ⚙️ System Requirements

- Windows 10 or Windows 11
- Python 3.12 for building from source
- Microphone for voice interaction
- Internet connection for cloud AI and online speech recognition
- Ollama installation for local AI

## 🚧 Project Status

JARVIS is an actively developing personal desktop assistant project. Features and compatibility may change as development continues.

## 👨‍💻 Developer

Created as a personal AI assistant project.

## 📜 License

Choose and add an open-source license before allowing others to reuse or distribute this project.
