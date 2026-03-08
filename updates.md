## SYSTEM CONTEXT

You are a **Senior ML Engineer + Full Stack Developer**. Generate a fully working, runnable **Emotion-Based Movie Recommender** for VSCode. Follow each phase **in exact order**. Every file must be complete and runnable — no placeholders, no TODOs.

---

## ✅ PHASE 1 — Project Scaffold (Run First)

Generate a shell script `setup.sh` that:

1. Creates the full folder structure:
```
movie-emotion-recommender/
├── app/__init__.py, routes.py, config.py
├── app/services/emotion_service.py, recommendation_service.py
├── ml/emotion_model.py, face_detector.py, preprocess.py
├── recommender/movie_loader.py, hybrid_recommender.py
├── quiz/quiz_engine.py, questions.py
├── data/, models/, static/css, static/js, templates/
├── run.py, requirements.txt, .env
```
2. Creates a Python **virtual environment**: `python -m venv venv`
3. Prints activation instructions for Windows/Mac/Linux

**Execute this first before anything else.**

---

## ✅ PHASE 2 — Requirements & Environment

Generate `requirements.txt` with exact pinned versions for:
- Flask, flask-cors
- torch, torchvision (CPU build)
- opencv-python-headless
- mediapipe
- scikit-learn, pandas, numpy
- requests, python-dotenv
- efficientnet_pytorch

Generate `.env`:
```
TMDB_API_KEY=your_tmdb_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

**Run:** `pip install -r requirements.txt`

---

## ✅ PHASE 3 — Sample Movie Dataset

Generate `data/movies_dataset.csv` with **50 real movies**, columns:
```
id, title, year, genre, overview, emotion_tags, rating, tmdb_id
```

Map emotions to movies:
- `happy` → comedy, adventure, animation
- `sad` → drama, romance
- `angry` → action, thriller
- `fear` → horror, thriller
- `neutral` → documentary, sci-fi
- `surprise` → mystery, fantasy
- `disgust` → dark comedy, satire

Include real titles like The Dark Knight, Interstellar, La La Land, etc.

---

## ✅ PHASE 4 — ML Emotion Detection Pipeline

Generate these files **in order**:

**4a. `ml/preprocess.py`**
- Face crop, resize to 224×224, normalize for EfficientNet

**4b. `ml/face_detector.py`**
- MediaPipe face detection
- Returns bounding box + cropped face image
- Fallback to OpenCV Haar if MediaPipe fails

**4c. `ml/emotion_model.py`**
- EfficientNet-B0 with custom head:
  - GlobalAvgPool → Dense(256) → Dropout(0.4) → Softmax(7)
- `load_model(path)` function
- `predict_emotion(face_img)` → returns `{emotion, confidence, probabilities}`
- If no trained model exists, use a **pretrained fallback** that maps face brightness/color features to emotions (so app runs without training)

**4d. `ml/train_model.py`**
- Full training script for FER2013
- Data augmentation (flip, rotate, brightness)
- EarlyStopping + LR scheduler
- Saves to `models/emotion_model.pt`
- **This is optional** — app must work without running this

---

## ✅ PHASE 5 — Quiz System

**5a. `quiz/questions.py`**
- 5 questions, 4 options each
- Each option has emotion weight dict:
```python
{"happy": 0.8, "neutral": 0.2}
```

**5b. `quiz/quiz_engine.py`**
- `calculate_emotion(answers)` → weighted scoring → returns top emotion + confidence score

---

## ✅ PHASE 6 — Hybrid Recommender

**6a. `recommender/movie_loader.py`**
- Load `movies_dataset.csv`
- Cache in memory after first load

**6b. `recommender/hybrid_recommender.py`**
- `get_recommendations(emotion, top_n=10)`:
  1. Filter movies by emotion_tags
  2. TF-IDF vectorize on genre + overview
  3. Cosine similarity ranking
  4. Return top 10 with TMDB poster URLs
- `fetch_tmdb_poster(tmdb_id)` using `.env` API key
- Graceful fallback if TMDB key missing (use placeholder image)

---

## ✅ PHASE 7 — Flask Backend

**7a. `app/config.py`**
- Load from `.env`
- Dev/Prod config classes

**7b. `app/services/emotion_service.py`**
- Wraps ml pipeline
- Accepts base64 image → returns emotion dict

**7c. `app/services/recommendation_service.py`**
- Wraps hybrid recommender

**7d. `app/routes.py`** — REST API:
```
GET  /           → index.html
GET  /quiz        → quiz.html  
GET  /camera      → camera.html
GET  /results     → results.html

POST /api/quiz            → {answers} → {emotion, confidence}
POST /api/detect-emotion  → {image_base64} → {emotion, confidence, probabilities}
GET  /api/recommendations?emotion=happy → [{title, poster, rating, ...}]
```

**7e. `app/__init__.py`**
- Flask app factory
- Register blueprints
- CORS enabled

**7f. `run.py`**
- Entry point: `python run.py`

---

## ✅ PHASE 8 — Netflix-Style Frontend

Generate all templates using **TailwindCSS CDN** (no build step needed).

**8a. `templates/base.html`**
- Dark theme (`#0f0f0f` background)
- Red accent color (`#e50914` Netflix red)
- Navigation bar: Logo + Quiz + Camera links
- TailwindCSS CDN link

**8b. `templates/index.html`**
- Full-screen hero with gradient background
- Title: *"Discover Movies That Match Your Mood"*
- Two CTA buttons: `Take Mood Quiz` | `Use Camera`
- Animated floating cards showing sample movies below hero

**8c. `templates/quiz.html`**
- One question shown at a time
- Animated progress bar at top
- Answer cards with hover glow effect
- Next/Previous navigation
- Submit button on last question
- JS handles transitions between questions

**8d. `templates/camera.html`**
- Live webcam preview (getUserMedia)
- Animated scan ring overlay on face
- "Capture & Detect" button
- Displays: detected emotion + confidence bar + emoji
- Canvas used to capture frame → base64 → POST to API

**8e. `templates/results.html`**
- Receives emotion from previous page (localStorage)
- Calls `/api/recommendations?emotion=X`
- Netflix-style horizontal scrollable movie grid
- Each card: poster, title, year, rating stars, genre badge
- Hover: card lifts + shows overview overlay
- "Detected Mood: 😊 Happy (87%)" badge at top

**8f. `static/js/main.js`**
- Quiz logic: question flow, answer collection, form submit
- Camera: webcam init, capture, base64 encode, API call
- Results: fetch recommendations, render cards
- Loading spinner during all API calls

**8g. `static/css/style.css`**
- Custom animations (scan pulse, card hover, fade-in)
- Glassmorphism card style
- Scrollbar styling

---

## ✅ PHASE 9 — Run & Test Checklist

Generate a `README.md` with these **exact terminal commands in order**:

```bash
# 1. Clone / open project in VSCode
cd movie-emotion-recommender

# 2. Create virtual environment
python -m venv venv

# 3. Activate (choose your OS)
# Windows:   venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Add TMDB key to .env (optional but recommended)
# Edit .env → TMDB_API_KEY=your_key

# 6. Run the app
python run.py

# 7. Open browser
# http://localhost:5000
```

---

## ✅ PHASE 10 — Error Resilience Rules

Every component must follow these rules:
- App **must run without a trained model** (use rule-based fallback)
- App **must run without TMDB key** (use placeholder posters)
- All API routes return proper JSON errors with status codes
- Camera page handles: no webcam, permission denied, detection failure
- Quiz works fully with keyboard navigation

---

## FINAL OUTPUT ORDER

Generate files **strictly in this sequence** so each file can be tested before the next:

1. `setup.sh`
2. `requirements.txt` + `.env`
3. `data/movies_dataset.csv`
4. `ml/preprocess.py` → `face_detector.py` → `emotion_model.py`
5. `quiz/questions.py` → `quiz_engine.py`
6. `recommender/movie_loader.py` → `hybrid_recommender.py`
7. `app/config.py` → `services/` → `routes.py` → `__init__.py` → `run.py`
8. `templates/base.html` → `index.html` → `quiz.html` → `camera.html` → `results.html`
9. `static/js/main.js` → `static/css/style.css`
10. `README.md`

**After each phase, confirm it is complete before proceeding to the next.**
