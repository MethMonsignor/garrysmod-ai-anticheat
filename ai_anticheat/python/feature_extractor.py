# python/feature_extractor.py

import os
import json
import numpy as np
import pandas as pd

# Known cheat module identifiers
cheat_modules = {"cheat_mod_0", "cheat_mod_1", "cheat_mod_2"}

def extract_features(entries):
    df = pd.DataFrame(entries)
    df['dt'] = df['time'].diff().clip(lower=1e-3)
    df['dpos'] = np.linalg.norm(df[['pos_x','pos_y','pos_z']].diff(), axis=1)
    df['dangles'] = np.linalg.norm(df[['pitch','yaw','roll']].diff(), axis=1)
    df['speed'] = df['dpos'] / df['dt']
    df['ang_rate'] = df['dangles'] / df['dt']
    df['packet_rate'] = df['packet_count'].diff() / df['dt']
    df['reaction_time'] = df['shot_time'].diff().fillna(np.nan)
    df['los_violation'] = df['target_visible'].apply(lambda x: 0 if x else 1)
    df['model_hash_mismatch'] = df['model_hash'] != df['expected_model_hash']
    df['module_inject'] = df['loaded_modules'].apply(
        lambda mods: any(m in cheat_modules for m in mods)
    )
    df['jitter'] = df['ping'].rolling(5).std().fillna(0)
    return df.fillna(0)

def build_feature_csv(log_dir, output_csv):
    rows = []
    for fname in os.listdir(log_dir):
        data = json.load(open(os.path.join(log_dir, fname)))
        feats = extract_features(data['entries'])
        feats['label'] = data['meta']['vector']
        rows.append(feats)
    pd.concat(rows).to_csv(output_csv, index=False)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--log_dir', required=True)
    p.add_argument('--output', default='features_all.csv')
    args = p.parse_args()
    build_feature_csv(args.log_dir, args.output)
