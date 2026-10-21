#!/usr/bin/env python3
"""Offline deterministic security, syntax and regression checks."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def check() -> None:
    for path in list((ROOT/'backend').rglob('*.py')) + list((ROOT/'scripts').glob('*.py')) + list((ROOT/'tests').rglob('*.py')):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    tasks = json.loads((ROOT/'engineering/tasks.json').read_text(encoding='utf-8'))
    ids = [t['id'] for t in tasks]
    assert len(ids) == len(set(ids)) and ids, 'Unique task IDs required'
    assert all(t['status'] in {'planned','review','done'} for t in tasks)
    for w in (ROOT/'.github/workflows').glob('*.yml'):
        wf = w.read_text(encoding='utf-8')
        assert 'pull_request_target:' not in wf
        assert 'contents: write' not in wf
        assert 'dangerously-bypass' not in wf
    sys.path.insert(0, str(ROOT))
    from backend.nayvelo.server import SIMULATION_ONLY
    assert SIMULATION_ONLY is True, 'Never enable telecom integration in mock service'
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'], cwd=ROOT, check=True)
    print('\nNAYVELO gates PASSED: syntax, task queue, CI permissions, offline unit/integration tests.')

if __name__=='__main__':
    check()
