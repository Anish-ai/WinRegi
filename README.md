# AI-Powered Windows Settings Explorer (WinRegi)

## 🚀 Project Overview
WinRegi is an **intelligent desktop application** built using **PyQt** and **Python**, designed to help users **explore and modify Windows settings effortlessly**. With an **AI-integrated search feature**, users can find settings based on natural language queries instead of exact keywords and securely manage **Windows Registry, PowerShell, and Control Panel settings**.

### 🎯 **Why This Project?**
Finding the right Windows settings can be frustrating due to:  
✅ A vast number of system settings.  
✅ Different categories and locations of settings.  
✅ Need to remember exact technical terms.

**Solution:** A **smart, AI-powered search assistant** that allows users to type what they want in simple words and **instantly get relevant settings**!

---
## 🛠️ **Tech Stack**
### 🔹 **Backend**
- **Python** (Main logic, AI processing, Windows API interaction)
- **PyQt** (GUI framework for desktop app development)
- **Windows API & Registry Access** (For settings modification)
- **Natural Language Processing (NLP)** (Using **spaCy** or **NLTK**) for AI-powered search
- **SQLite** (For storing thousands of pre-defined settings in a structured format)

### 🔹 **Frontend (UI)**
- **PyQt Designer** (For visually designing UI)
- **Custom Widgets** (For a modern look and feel)
- **Light/Dark Theme Support** 🌙 ☀️
- **Categorized Settings** (For easier navigation)
- **Dedicated UI for Every Setting** (Ensuring easy interaction)

---
## 🏗️ **How It Works?**
1. **Settings Database** 📂
   - The app maintains a structured database of Windows settings and their corresponding access methods (Registry edits, Control Panel links, PowerShell commands, etc.).
   - This database contains **thousands of pre-stored settings**, each structured with relevant UI components.
2. **AI Search Engine** 🔍
   - Users can type queries like:
     - "How to make my PC faster?"
     - "Enable dark mode"
     - "Stop background apps"
   - The AI maps these queries to relevant Windows settings.
3. **Action Flow with User Control** 🛠️
   - **AI will NOT directly perform actions that require multiple changes**.
   - Instead, it will suggest all required changes and let the user choose.
   - Users can **review and confirm** actions before executing them.
   - **New Feature: AI Auto-Apply Mode** ⚡
     - Experienced users can enable **AI Auto-Apply Mode**, where the AI applies recommended changes automatically with a confirmation prompt.
   - **Security Enhancements** 🔒
     - Added an AI validation layer to prevent harmful or unintended modifications.

---
## 📌 **Features**
✅ **AI-Powered Search**: No need to remember exact names of settings. Just describe what you want.  
✅ **Quick Actions**: Modify settings instantly from the app.  
✅ **Deep Windows Integration**: Uses Windows API, Registry, and PowerShell for control.  
✅ **Categorized Settings**: Organizes thousands of Windows settings into sections.  
✅ **User-Friendly UI**: Built with PyQt for a smooth experience.  
✅ **Favorites & History**: Keep track of most-used settings.  
✅ **Dedicated UI for Each Setting**: Users can navigate through a visually rich interface for each setting.  
✅ **AI Suggestions Instead of Direct Actions**: Ensures user has full control over modifications.  
✅ **Pre-Stored Settings Database**: Thousands of Windows settings pre-loaded for easy access.  
✅ **Light/Dark Theme Support**: Switch between themes for better usability.  
✅ **Expanded Settings Database** 📊: Now includes **more Group Policy settings and PowerShell automation scripts**.  

---
## 🖥️ **Installation Guide**

### 📌 **Prerequisites**
- Windows 10/11
- Python 3.8+
- pip
- Virtual Environment (recommended)

### 🛠️ **Setup**
```bash
# Clone the repository
git clone https://github.com/your-repo/windows-settings-explorer.git
cd windows-settings-explorer

# Create a virtual environment
python -m venv env
source env/bin/activate  # For Linux/macOS
env\Scripts\activate    # For Windows

# Install dependencies
pip install -r requirements.txt
```

---
## 🚀 **Usage**
```bash
python main.py
```
- Use the search bar to **type your query**.
- Click on suggested settings to **review and customize them**.
- Browse through categorized settings for easy access.

---
## 📂 **Project Structure**
- `ai_engine/` - NLP processing and search functionality
- `database/` - SQLite database management
- `ui/` - PyQt5 user interface components
- `windows_api/` - Windows registry and settings management

---
## 🔧 **Example Queries & Responses**
| **User Query** | **Suggested Settings & Actions** |
|--------------|----------------|
| "Turn on night mode" | ✅ Open Night Light settings UI with options to customize |
| "Make text bigger" | ✅ Show accessibility settings with slider control |
| "Disable background apps" | ✅ List background apps, let user toggle which to disable |
| "Improve battery life" | ✅ Suggest power settings adjustments, allow user to apply changes |
| "Speed up PC" | ✅ Recommend startup app removal, service tweaks, and performance settings |

---
## 📚 **Where We Get Windows Settings & Methods**
We gather Windows settings from multiple sources:
- **Windows Registry Keys** 🗝️
- **Group Policy Settings (gpedit.msc)** 📜
- **Control Panel & PowerShell Commands** ⚡
- **Windows Settings URLs (ms-settings://)** 🏗️
- **Public Microsoft Documentation** 📄
- **Pre-Stored Structured Database** 📊 (Containing thousands of Windows settings)

---
## 💡 **Future Improvements**
🔹 **Voice-Based Search** 🎙️ (Find settings with voice commands)  
🔹 **User Preferences** (Customize settings based on usage patterns)  
🔹 **Integration with Windows Assistant (Cortana)** 🤖  
🔹 **Smart Recommendations** (Suggest optimizations based on usage)  

---
## 🤝 **Contributing**
Want to help improve the project? Follow these steps:
1. **Fork the Repository** 🍴
2. **Create a Feature Branch** (`git checkout -b feature-name`)
3. **Commit Your Changes** (`git commit -m "Added new feature"`)
4. **Push to Your Branch** (`git push origin feature-name`)
5. **Submit a Pull Request** 🚀

---
## 📜 **License**
This project is licensed under the **MIT License**. Feel free to use and modify it! 🎉

---
## 📧 **Contact**
👤 **Developer**: Anish Kumar  
📩 Email: aniskum59431@gmail.com  
🔗 GitHub: [Anish-ai](https://github.com/Anish-ai)  
🔗 LinkedIn: [Anish Kumar](https://www.linkedin.com/in/anish-kumar-71779326a/)  

---
_🚀 Made with ❤️ to make Windows settings easier for everyone!_