#!/usr/bin/env python3
"Safe, one-task-at-a-time Codex orchestrator: never auto-merge or deploy."
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SENSITIVE = ('AGENTS.md', 'engineering/RELEASE_GATES.md', '.github/', '.env', 'secrets/', 'deploy/', 'infrastructure/', 'scripts/', 'tests/test_server.py')

def git(*args: str, capture: bool=False) -> str:
    out = subprocess.run(['git', *args], cwd=ROOT, text=True, capture_output=capture, check=True)
    return out.stdout.strip() if capture else ''

def changed_files() -> list[str]:
    tracked = git('diff', '--name-only', 'HEAD', capture=True).splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard', capture=True).splitlines()
    return sorted(set(tracked + untracked))

def main() -> None:
    p=argparse.ArgumentParser(description='NAYVELO task runner (dry run by default)')
    p.add_argument('--execute',action='store_true',help='run Codex on feature branch and validate')
    p.add_argument('--commit',action='store_true',help='commit gated results to feature branch')
    p.add_argument('--push',action='store_true',help='push committed feature branch to origin')
    p.add_argument('--draft-pr',action='store_true',help='create draft PR using GitHub CLI')
    p.add_argument('--task',help='specific planned task ID')
    a=p.parse_args()
    if a.commit and not a.execute or a.push and not a.commit or a.draft_pr and not a.push:
        p.error('--draft-pr requires --push, --push requires --commit and --commit requires --execute')
    tasks=json.loads((ROOT/'engineering/tasks.json').read_text(encoding='utf-8'))
    in_review=[t for t in tasks if t['status']=='review']
    if in_review and not a.task:
        print('Paused: task in review. Merge and mark done, or explicitly select a planned task.')
        return
    selected=[t for t in tasks if t['status']=='planned' and (not a.task or t['id']==a.task)]
    if not selected:
        print('No planned task found.')
        return
    t=sorted(selected,key=lambda x:x['priority'])[0]
    branch='feature/'+t['id'].lower()+'-'+re.sub('[^a-z0-9]+','-',t['title'].lower()).strip('-')[:48]
    prompt = f'''Implement NAYVELO task {t['id']}: {t['title']}.\n\nAcceptance criteria:\n'''+''.join(f"- {x}\n" for x in t['acceptance'])+'''\nRead AGENTS.md, engineering/RELEASE_GATES.md and relevant existing tests. Work only on this task. Keep SIMULATION_ONLY fail-closed. Add positive and negative regression tests. Run python3 scripts/validate.py. Do not touch AGENTS.md, CI, release gates, secrets, deployments or remote systems. Do not git commit, push, create PR, merge or deploy. Conclude with a concise summary and test results.'''
    print(f'NEXT TASK: {t["id"]} — {t["title"]}\nBRANCH: {branch}')
    if not a.execute:
        print('DRY RUN only. Use --execute after reviewing AGENTS.md and RELEASE_GATES.md.\nPROMPT:\n'+prompt)
        return
    if not shutil.which('git') or not shutil.which('codex'):
        raise SystemExit('Required tools: git and authenticated codex CLI.')
    if git('rev-parse', '--is-inside-work-tree', capture=True) != 'true':
        raise SystemExit('Initialize and commit a git repository before running an agent.')
    base=git('branch', '--show-current', capture=True)
    if base not in ('main','develop'):
        raise SystemExit('Execute only on clean main/develop; review existing feature branches first.')
    if git('status', '--porcelain', capture=True):
        raise SystemExit('Working directory is not clean. Commit or stash changes first.')
    git('switch', '-c', branch)
    print('Running Codex with workspace-write sandbox (no privileged access).')
    result=subprocess.run(['codex','exec','--sandbox','workspace-write','--cd',str(ROOT),'-'],input=prompt,text=True,cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit('Codex failed. Inspect local feature branch; no push or PR performed.')
    changed=changed_files()
    if not changed:
        raise SystemExit('No code changes. Nothing to commit or publish.')
    sensitive=[f for f in changed if any(f==s or f.startswith(s) for s in SENSITIVE)]
    if sensitive:
        raise SystemExit(f'BLOCKED: sensitive paths changed: {sensitive}. Manual review required; no push or PR.')
    print('Changed files:',', '.join(changed))
    subprocess.run([sys.executable,'scripts/validate.py'],cwd=ROOT,check=True)
    if a.commit:
        # A task is marked done only on the feature branch. Main advances only after reviewed PR merge.
        t['status']='done'
        (ROOT/'engineering/tasks.json').write_text(json.dumps(tasks,indent=2)+'\n',encoding='utf-8')
        remaining=sorted((x for x in tasks if x['status']=='planned'),key=lambda x:x['priority'])
        if remaining:
            n=remaining[0]
            next_body=f"# {n['id']} — {n['title']}\n\nStatus: planned\n\nAcceptance criteria:\n"+''.join('- '+v+'\n' for v in n['acceptance'])+"\nRead AGENTS.md and engineering/RELEASE_GATES.md. Maintain SIMULATION_ONLY.\n"
        else:
            next_body='# NAYVELO Queue Complete\n\nNo planned tasks; propose new work by reviewed engineering decision.\n'
        (ROOT/'engineering/NEXT_TASK.md').write_text(next_body,encoding='utf-8')
        subprocess.run([sys.executable,'scripts/validate.py'],cwd=ROOT,check=True)
        git('add', '--', *changed, 'engineering/tasks.json', 'engineering/NEXT_TASK.md')
        git('commit', '-m',f'{t["id"]}: {t["title"]} (validated draft)')
        if a.push:
            git('push', '--set-upstream', 'origin', branch)
            if a.draft_pr:
                if not shutil.which('gh'):
                    raise SystemExit('Push succeeded; gh CLI missing. Create a draft PR manually.')
                subprocess.run(['gh','pr','create','--draft','--base',base,'--head',branch,
                    '--title',f'{t["id"]}: {t["title"]}',
                    '--body','Automated implementation. All tests must pass in GitHub CI. Human review required. No telecom activation, payments, or deployment.'],cwd=ROOT,check=True)
    else:
        print('Changes remain uncommitted on the feature branch for review.')
    print('Validation passed. No merge or deployment performed.')

if __name__=='__main__':
    main()
