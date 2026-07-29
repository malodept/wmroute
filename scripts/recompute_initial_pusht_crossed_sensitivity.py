#!/usr/bin/env python3
"""Recompute the V106 crossed state-by-seed sensitivity from released rows."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_COLUMN = "pusht_prediction_interface_sequential_router_cost"
REFERENCES = [
    ("Fixed Medium", "fixed_medium_cost"),
    ("Fixed Full", "fixed_full_cost"),
    ("Task-only input router", "task_only_input_router_cost"),
    ("Margin sequential matched-rate", "margin_sequential_matched_rate_cost"),
    ("Expected random input matched-rate", "expected_random_input_matched_rate_cost"),
]
def parse_args():
    p=argparse.ArgumentParser(); p.add_argument('--per-state',type=Path,default=ROOT/'artifacts/v106/per_state_primary.csv'); p.add_argument('--output',type=Path,default=ROOT/'artifacts/v106/repaired_inference'); p.add_argument('--repeats',type=int,default=20000); p.add_argument('--seed',type=int,default=10603); p.add_argument('--upper-quantile',type=float,default=.99); return p.parse_args()
def crossed_draws(values,repetitions,seed):
    n_states,n_seeds=values.shape; rng=np.random.default_rng(seed); out=np.empty(repetitions); chunk_size=256
    for start in range(0,repetitions,chunk_size):
        end=min(start+chunk_size,repetitions); c=end-start
        seed_pos=rng.integers(0,n_seeds,size=(c,n_seeds)); state_idx=rng.integers(0,n_states,size=(c,n_states))
        sampled = values[state_idx[:, :, None], seed_pos[:, None, :]]
        out[start:end] = sampled.mean(axis=(1, 2))
    return out
def main():
    a=parse_args(); df=pd.read_csv(a.per_state); seeds=sorted(map(int,df.upstream_model_seed.unique())); states=sorted(map(int,df.global_state_id.unique()))
    if (len(seeds),len(states))!=(3,1600): raise RuntimeError((len(seeds),len(states)))
    rows=[]
    for idx,(ref,col) in enumerate(REFERENCES):
        cols=[]
        for s in seeds:
            part=df[df.upstream_model_seed==s].sort_values('global_state_id')
            if list(map(int,part.global_state_id))!=states: raise RuntimeError(f'state mismatch seed {s}')
            cols.append(part[CANDIDATE_COLUMN].to_numpy(float)-part[col].to_numpy(float))
        values=np.stack(cols,axis=1); draws=crossed_draws(values,a.repeats,a.seed+100+idx)
        rows.append({'candidate':'PushT prediction-interface sequential router','reference':ref,'lambda':.002,'cost_difference_candidate_minus_reference':float(values.mean()),'sensitivity_q025':float(np.quantile(draws,.025)),'sensitivity_q975':float(np.quantile(draws,.975)),'adjusted_one_sided_upper_quantile':float(np.quantile(draws,a.upper_quantile)),'adjusted_upper_below_zero':bool(np.quantile(draws,a.upper_quantile)<0.0),'crossed_state_vector_shared_across_sampled_seeds':True,'sensitivity_repetitions':a.repeats,'sensitivity_seed':a.seed+100+idx,'population_confidence_interval':False})
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'crossed_seed_state_sensitivity.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary={'status':'V106_POST_AUDIT_CROSSED_SENSITIVITY_COMPLETE','input':str(a.per_state),'states':len(states),'model_seeds':seeds,'repetitions':a.repeats,'base_seed':a.seed,'upper_quantile':a.upper_quantile,'state_resampling':'one shared physical-state index vector per replicate across every sampled model-seed position','interpretation':'empirical 2.5%-97.5% crossed seed/state sensitivity quantiles over the observed three-checkpoint distribution; not confidence coverage for a broader training-run population'}
    (a.output/'repair_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
