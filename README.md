# 📹 MedicalSkillsRecorder

MedicalSkillsRecorder is a video recording system designed for capturing participant responses in a structured evaluation framework. This tool provides a **secure** and **controlled** environment for video collection, ensuring privacy and reproducibility.

---

## 🚀 Features
- **Web-based interface** for recording short response videos.
- **Secure storage** with SSL support.
- **Dockerized deployment** for easy setup.
- **Integrated dataset storage** for evaluation results.

---

## 📁 Project Structure
```
MedicalSkillsRecorder/
│── data/                     # Anonymized evaluation datasets
│   │── skills.csv             # Evaluation results
│   │── feedback.csv           # User feedback
│── src/                      # Source code
│   │── app.py                 # Main application script
│   │── .env                   # Environment variables (NOT INCLUDED)
│   │── transcription.txt      # Transcription of the video which is used in the prompt for the questions generation
│   │── ssl/                   # SSL certificates (for local HTTPS)
│   └── uploaded_files/        # Storage for recorded videos
│── docker-compose.yml        # Docker configuration
│── Dockerfile                # Docker image setup
│── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🔧 Installation & Usage

### **1️⃣ Prerequisites**
- Docker installed
- Python 3.8+ (if running manually)
- An **OpenAI API Key** for accessing OpenAI services.

### How to Get Your OpenAI API Key

1. Go to the [OpenAI API Keys](https://platform.openai.com/account/api-keys) page.
2. Sign in or create an OpenAI account if you don’t already have one.
3. Click "Create new secret key" to generate a new API key.
4. Copy the API key and paste it into the `OPENAI_API_KEY` field in your `.env` file.

### **2️⃣ Running with Docker**
```bash
docker-compose up --build
```
This will launch the web interface on `https://localhost:5000`.

### **3️⃣ Running Manually**
```bash
pip install -r requirements.txt
python src/app.py
```

---

## 📊 Datasets
This repository includes anonymized evaluation results:

### **📄 skills.csv** (Evaluation Results)
- **Contains:** Performance data for transversal skill assessment.
- **Columns:**
  - `ID`: Unique identifier
  - `career`, `semester`: Participant info (anonymized)
  - `clinical_reasoning_label`, `clinical_reasoning_value`
  - `conflict_resolution_label`, `conflict_resolution_value`
  - `leadership_label`, `leadership_value`
  - `stress_control_label`, `stress_control_value`

### **📄 feedback.csv** (User Feedback)
- **Contains:** User responses on system usability.
- **Columns:**
  - `ID`: Unique feedback entry
  - `Q1_decision_making`: Likert-scale score (1-5)
  - `Q2_feedback_clarity`: Likert-scale score (1-5)

---

## 🛑 Privacy & Ethical Considerations
- **No personal data is stored**.
- **Videos are saved locally** and are not included in this dataset.
- **Anonymized results** ensure compliance with ethical research standards.

---

## 📌 Citation
If you use this tool, please reference this repository appropriately.

📁 **Repository:** MedicalSkillsRecorder  
✅ **Last updated:** March 2025

