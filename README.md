# 🎬 Movie Recommender System

An AI-powered movie recommendation system that uses **emotion detection** to suggest personalized movies based on your current mood.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0.1-red)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🎭 **Emotion Detection**: Uses deep learning (EfficientNet-B0) to detect 7 emotions
- 📝 **Interactive Quiz**: Answer questions to determine your current mood
- 📸 **Camera Detection**: AI analyzes your facial expression in real-time
- 🤖 **Hybrid Recommender**: Combines TF-IDF and cosine similarity for accurate recommendations
- 🌐 **TMDB Integration**: Fetches real movie posters and data
- 🎨 **Netflix-style UI**: Modern, responsive interface with TailwindCSS
- ⚡ **Fast & Efficient**: Modular architecture with caching

## 🎯 Detected Emotions

- **Happy** 😊
- **Sad** 😢
- **Angry** 😠
- **Fear** 😨
- **Neutral** 😐
- **Surprise** 😲
- **Disgust** 🤢

## 🏗️ Architecture

```
movie-recommender/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration
│   ├── routes.py                # API routes
│   └── services/                # Business logic
│       ├── emotion_service.py   # Emotion detection
│       └── recommendation_service.py
├── ml/                          # Machine learning pipeline
│   ├── emotion_model.py         # EfficientNet-B0 model
│   ├── face_detector.py         # MediaPipe + OpenCV
│   ├── preprocess.py            # Image preprocessing
│   └── train_model.py           # Training script (optional)
├── quiz/                        # Quiz system
│   ├── questions.py             # Quiz questions
│   └── quiz_engine.py           # Scoring algorithm
├── recommender/                 # Recommendation engine
│   ├── movie_loader.py          # CSV data loader
│   └── hybrid_recommender.py    # TF-IDF + cosine similarity
├── data/
│   └── movies_dataset.csv       # 70 movies with TMDB IDs
├── templates/                   # Jinja2 templates
├── static/                      # CSS, JS, images
└── run.py                       # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **TMDB API Key** (optional, for movie posters)

### Installation

#### Option 1: Automatic Setup (Windows)

```powershell
# Run setup script
.\setup.ps1
```

#### Option 2: Automatic Setup (Linux/macOS)

```bash
# Run setup script
chmod +x setup.sh
./setup.sh
```

#### Option 3: Manual Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd movie-recommender
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file:
```env
TMDB_API_KEY=your_api_key_here
FLASK_ENV=development
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=5000
```

**Get TMDB API Key**: [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

5. **Run the application**
```bash
python run.py
```

6. **Open browser**
```
http://localhost:5000
```

## 📖 Usage

### 1. Quiz Method
1. Click **"Take Quiz"** on the homepage
2. Answer 5 questions about your current mood
3. Get personalized movie recommendations

### 2. Camera Method
1. Click **"Use Camera"** on the homepage
2. Allow camera permissions
3. Click **"Detect Emotion"**
4. View recommended movies based on your facial expression

## 🧠 How It Works

### Emotion Detection Pipeline

```
Input Image → Face Detection → Preprocessing → EfficientNet-B0 → Emotion Classification
```

1. **Face Detection**: MediaPipe (primary) + OpenCV Haar Cascade (fallback)
2. **Preprocessing**: 224×224 resize, ImageNet normalization, CLAHE contrast enhancement
3. **Model**: EfficientNet-B0 with custom classification head
4. **Fallback**: Rule-based emotion detection using brightness/contrast analysis

### Recommendation Pipeline

```
Emotion → Filter Movies → TF-IDF Vectorization → Cosine Similarity → Rank by Rating → TMDB Posters
```

1. **Filter**: Select movies matching detected emotion
2. **Vectorize**: TF-IDF on genre + overview text
3. **Rank**: Sort by rating and diversity
4. **Enhance**: Fetch posters from TMDB API

## 🎓 Training Your Own Model (Optional)

The system includes a training script for the FER2013 dataset:

```bash
python -m ml.train_model
```

**Requirements**:
- FER2013 dataset (download from Kaggle)
- GPU recommended (CUDA support)
- ~2-3 hours training time

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TMDB_API_KEY` | - | TMDB API key for movie posters |
| `FLASK_ENV` | `development` | Environment mode |
| `SECRET_KEY` | `dev-secret-key` | Flask session secret |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `5000` | Server port |

### Model Settings

Edit `app/config.py` to customize:
- Number of recommendations (`TOP_N_RECOMMENDATIONS`)
- Supported emotions (`EMOTIONS`)
- Model paths (`MODEL_PATH`)
- Upload limits (`MAX_CONTENT_LENGTH`)

## 📊 Dataset

The project includes a curated dataset of **70 movies** with:
- **Columns**: id, title, year, genre, overview, emotion_tags, rating, tmdb_id
- **Genres**: Action, Drama, Comedy, Horror, Sci-Fi, Romance, Animation
- **Emotions**: All 7 emotions covered with 10+ movies each

**Format**: CSV (`data/movies_dataset.csv`)

## 🛠️ Tech Stack

### Backend
- **Flask 2.3.3**: Web framework
- **PyTorch 2.0.1**: Deep learning
- **EfficientNet**: Pre-trained model
- **MediaPipe 0.10.3**: Face detection
- **scikit-learn 1.3.0**: TF-IDF, cosine similarity
- **pandas 2.0.3**: Data manipulation

### Frontend
- **TailwindCSS**: Utility-first CSS
- **Vanilla JavaScript**: No heavy frameworks
- **Jinja2**: Server-side templating

### APIs
- **TMDB API**: Movie data and posters

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **EfficientNet**: [Google Research](https://github.com/tensorflow/tpu/tree/master/models/official/efficientnet)
- **MediaPipe**: [Google MediaPipe](https://google.github.io/mediapipe/)
- **TMDB**: [The Movie Database](https://www.themoviedb.org/)
- **FER2013**: Facial Expression Recognition dataset

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ using PyTorch, Flask, and AI**
