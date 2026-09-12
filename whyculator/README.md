# WHYculator – The Useless Calculator

![Whyculator Banner](https://raw.githubusercontent.com/example/whyculator/main/assets/banner.png)

## 🎯 Goal
**WHYculator** is a deliberately *useless* yet **premium‑looking** calculator. It pretends to respect the user’s requested operation only ~15 % of the time, adds chaotic “fun” modifications, and serves random AI‑style explanations, confidence scores, and excuses. Perfect for a college “Useless Project” hackathon where humor meets polished UI.

---
## ✨ Features
- **Randomized operation**: obeys the user’s request 15 % of the time, otherwise picks another operation.
- **Chaos mode**: optionally scrambles numbers, swaps operands, or changes the operation.
- **Premium UI**: dark theme, glass‑morphism cards, smooth micro‑animations, responsive mobile‑first design.
- **AI‑style reasoning**: random explanations, confidence scores, and confidence labels.
- **Easter eggs**: special responses for `69+69`, `0+0`, `1+1`, `404`, etc.
- **Statistics panel**: total calculations, ignored requests, uselessness %.
- **History list**: each calculation displayed with original and actual operation.
- **Excuse generator**: a button that returns a random excuse for why the calculator behaved oddly.
- **Reset flow**: clear stats and history.
- **Optional sound effects** (toggle on/off).

---
## 🛠️ Tech Stack
- **Backend**: Python 3.11+, Flask >=3.0
- **Frontend**: HTML5, vanilla CSS (glass‑morphism) & JavaScript (no frameworks)
- **Styling**: Google Font *Inter*, CSS variables, media queries, `prefers‑reduced‑motion`

---
## 📦 Installation
```bash
# Clone (or copy) the project into your workspace
# Assuming you are already in d:/tinkerhub
mkdir whyculator && cd whyculator

# Place the provided files (app.py, requirements.txt, etc.)
# Install dependencies
pip install -r requirements.txt
```

---
## 🚀 Running the app
```bash
# From the whyculator directory
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---
## 📖 Usage
1. Enter two numbers and pick an operation.
2. (Optional) Enable **Chaos mode** and/or **Sound effects**.
3. Click **Calculate** – watch the loader/roulette animation.
4. View the **Result**, confidence score, AI explanation, and any chaos message.
5. Check the **Stats** and **History** panels on the right.
6. Press **Generate Excuse** for a funny excuse.
7. Double‑click the header or use the hidden reset button to clear everything.

---
## 🧪 Testing / Verification
- Use `curl -X POST -H "Content-Type: application/json" -d '{"first_number":"10","second_number":"5","operation":"+","chaos_mode":false}' http://127.0.0.1:5000/calculate` to see JSON response.
- Verify that `/stats`, `/excuse`, and `/reset` endpoints return the expected data.
- Browse the UI on a desktop and a mobile width to confirm responsiveness.
- Ensure the app does **not** crash on division‑by‑zero or malformed input.

---
## 📚 Design notes
- All UI colors are defined with CSS variables for easy theme tweaking.
- The backend keeps all state in‑memory; statistics are lost when the server stops (perfect for a hackathon demo).
- The code is heavily commented for readability and future extension.

---
## 🙌 Credits
- Built by **Antigravity** (AI‑assisted coding) and the user for the *Useless Project* hackathon.
- Font: [Inter](https://fonts.google.com/specimen/Inter)
- Icons & emojis are from the standard Unicode set.

---
## 📜 License
This is a **fun, hackathon‑only** project. Feel free to copy, modify, and share it for educational or entertainment purposes.
