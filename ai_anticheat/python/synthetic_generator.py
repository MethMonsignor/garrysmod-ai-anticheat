# python/synthetic_generator.py

import os
import json
import numpy as np
from data_collector import record_session

CHEAT_CONFIG = {
    "teleport":      {"max_jump_dist":2000,"interval_mean":5,"duration":60},
    "wallhack":      {"occlusion_rate":0.3,"smoothness_sigma":5,"duration":60},
    "memory_injection":{"module_count":3,"inject_prob":0.7,"duration":60},
    "score_spoof":   {"stat_delta_mean":500,"stat_delta_std":200,"interval_mean":10,"duration":60},
    "ghost_inputs":  {"sequence_length":20,"time_shift_sigma":0.05,"duration":60}
}

def simulate_clean_play(duration):
    entries, t = [], 0.0
    last_pos = np.array([0.0,0.0,0.0])
    last_ang = np.array([0.0,0.0,0.0])
    while t < duration:
        dt = 0.1
        t += dt
        last_pos += np.random.normal(0,10,3)
        last_ang += np.random.normal(0,2,3)
        entries.append({
            "time": t,
            "pos_x": last_pos[0], "pos_y": last_pos[1], "pos_z": last_pos[2],
            "pitch": last_ang[0], "yaw": last_ang[1], "roll": last_ang[2],
            "packet_count": int(t * 20),
            "shot_time": t if np.random.rand()<0.05 else None,
            "target_visible": True,
            "model_hash": "default", "expected_model_hash": "default",
            "loaded_modules": [],
            "ping": np.random.normal(50,5)
        })
    return entries

def simulate_teleport(config):
    entries, t = [], 0.0
    last_pos = np.array([0.0, 0.0, 0.0])
    while t < config["duration"]:
        dt = np.random.exponential(config["interval_mean"])
        t += dt
        offset = np.random.uniform(-config["max_jump_dist"], config["max_jump_dist"], 3)
        new_pos = last_pos + offset
        entries.append({
            "time": t,
            "pos_x": new_pos[0], "pos_y": new_pos[1], "pos_z": new_pos[2],
            "pitch": 0, "yaw": 0, "roll": 0,
            "packet_count": int(t * 20),
            "shot_time": None,
            "target_visible": True,
            "model_hash": "default", "expected_model_hash": "default",
            "loaded_modules": [],
            "ping": np.random.normal(50,5)
        })
        last_pos = new_pos
    return entries

def simulate_wallhack(config):
    entries, t, last_ang = [], 0.0, np.array([0.0,0.0,0.0])
    while t < config["duration"]:
        dt = 0.1
        t += dt
        occluded = np.random.rand() < config["occlusion_rate"]
        ang_delta = np.random.normal(0, config["smoothness_sigma"], 3)
        new_ang = last_ang + ang_delta
        entries.append({
            "time": t,
            "pos_x": 0, "pos_y": 0, "pos_z": 0,
            "pitch": new_ang[0], "yaw": new_ang[1], "roll": new_ang[2],
            "packet_count": int(t * 20),
            "shot_time": t if occluded else None,
            "target_visible": not occluded,
            "model_hash": "default", "expected_model_hash": "default",
            "loaded_modules": [],
            "ping": np.random.normal(50,5)
        })
        last_ang = new_ang
    return entries

def simulate_memory_injection(config):
    entries = simulate_clean_play(config["duration"])
    for e in entries:
        if np.random.rand() < config["inject_prob"]:
            e["loaded_modules"] = [f"cheat_mod_{i}" for i in range(config["module_count"])]
    return entries

def simulate_score_spoof(config):
    entries = simulate_clean_play(config["duration"])
    t = 0.0
    while t < config["duration"]:
        dt = np.random.normal(config["interval_mean"], config["interval_std"])
        t += max(dt,0.1)
        delta = int(np.random.normal(config["stat_delta_mean"], config["stat_delta_std"]))
        entries.append({
            "time": t,
            "pos_x": 0, "pos_y": 0, "pos_z": 0,
            "pitch": 0, "yaw": 0, "roll": 0,
            "packet_count": int(t * 20),
            "shot_time": None,
            "target_visible": True,
            "model_hash": "default", "expected_model_hash": "default",
            "loaded_modules": [],
            "ping": np.random.normal(50,5),
            "score_delta": delta
        })
    return entries

def simulate_ghost_inputs(config):
    base_seq, t = [], 0.0
    for _ in range(config["sequence_length"]):
        dt = np.random.normal(0.05, config["time_shift_sigma"])
        t += max(dt, 0.01)
        base_seq.append({
            "time": t,
            "pos_x": np.random.uniform(-100,100),
            "pos_y": np.random.uniform(-100,100),
            "pos_z": np.random.uniform(0,50),
            "pitch": np.random.uniform(-180,180),
            "yaw": np.random.uniform(-180,180),
            "roll": 0,
            "packet_count": int(t * 20),
            "shot_time": None,
            "target_visible": True,
            "model_hash": "default", "expected_model_hash": "default",
            "loaded_modules": [],
            "ping": np.random.normal(50,5)
        })
    entries = []
    for e in base_seq:
        shift = np.random.normal(0, config["time_shift_sigma"])
        e2 = e.copy()
        e2["time"] = max(e["time"] + shift,0)
        entries.append(e2)
    return sorted(entries, key=lambda x: x["time"])

def generate_all_synthetic(output_dir="logs/synthetic"):
    os.makedirs(output_dir, exist_ok=True)
    for vector, cfg in CHEAT_CONFIG.items():
        sim_fn = globals()[f"simulate_{vector}"]
        entries = sim_fn(cfg)
        record_session(
            player_id="synthetic_"+vector,
            entries=entries,
            vector_type=vector,
            output_dir=output_dir
        )

if __name__ == "__main__":
    generate_all_synthetic()
    print("Synthetic sessions generated for:", ", ".join(CHEAT_CONFIG.keys()))
