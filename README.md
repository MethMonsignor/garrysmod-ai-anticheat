# garrysmod-ai-anticheat

## End to end AI driven anti cheat for Garry’s Mod

- Collects real & synthetic gameplay data  
- Extracts per tick features (speed, ang rate, jitter, etc.)  
- Trains RandomForest & IsolationForest models  
- Exposes a Flask-based `/predict` API  
- Integrates with GMod for instant SteamID perm bans & kicks


## Features

- Multi vector cheat detection (aimbot, speedhack, wallhack, teleport, etc.)

- Synthetic data generators for under-represented cheat types

- Unified feature extractor (speed, angular rate, packet jitter, LOS violations, module inject)

- Python pipeline: data collection → feature CSV → model training → Flask API

- Garry’s Mod Lua hooks for real-time feature gathering and HTTP POST to API

- Instant permanent bans by SteamID + immediate kick + banlist persistence

- CheckPassword hook to block reconnects

- Audit logging stub (logCheatEvent) for appeals and analytics

## What It Does

- Data Collection

- Records clean and cheat sessions to JSON logs (data_collector.py).

- Optionally spins up synthetic cheat logs (synthetic_generator.py).

- Feature Extraction

- Parses logs into per-tick metrics: speed, ang_rate, packet_rate, reaction_time, los_violation, module_inject, jitter (feature_extractor.py).

- Model Training

- Trains a multi-class RandomForest and an IsolationForest for anomaly detection (train_models.py).

- Prediction Service

- Serves POST /predict JSON API returning vector probabilities + anomaly score (api.py).

- GMod Integration

- Lua hook on PlayerTick gathers features and calls the API.

- If a vector exceeds its threshold or anomaly score is low, the player is immediately perm-banned and kicked (ai_anticheat.lua).

- ac_ban_check.lua blocks reconnect attempts for banned SteamIDs.

## Prerequisites

- Python 3.8+ installed and on your PATH.

- pip (Python package manager).

- A Garry’s Mod dedicated server with file-system access.

- Unix-style shell (Linux/macOS) or Windows PowerShell/CMD.

## Clone the Repository

cd ~
git clone https://github.com/yourusername/garrysmod-ai-anticheat.git
cd garrysmod-ai-anticheat

## Set Up Python Environment

Create a virtual environment:

- cd python python3 -m venv venv

Activate it:

- Linux/MAC: source venv/bin/activate

- Windows: venv\Scripts\activate

- Install dependencies: pip install --upgrade pip / pip install -r requirements.txt

- Build feature CSV: python feature_extractor.py --log_dir python/logs --output python/features_all.csv

- Train models: python train_models.py

- Launch the prediction API: python api.py / It will listen on 0.0.0.0:5000.

- Ensure cfg/banlist.cfg is writable. Start your server normally: ./srcds_run -game garrysmod +map gm_flatgrass +maxplayers 16

## Configuration

- Thresholds: Tweak per-vector probability thresholds in ai_anticheat.lua.

- API URL: Change http://127.0.0.1:5000/predict if hosting elsewhere.

- Audit Logging: Implement logCheatEvent in Lua to record bans to your database or file.

## Work In Progress

- Example clean play generator in synthetic_generator.py is a stub—replace with your own or extend realism.

- No unit tests yet; all code is untested in production.

- engine.GetModules() in Lua is hypothetical replace with actual module listing logic if available.

- Model explainability and appeal UI are TODOs.


