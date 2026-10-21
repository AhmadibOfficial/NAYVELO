# NAYVELO — Autonomous Engineering Starter

**Mobile, made digital.** Nigeria-first, eSIM-only telecom customer experience.

**Status: software prototype only.** This repository does not operate a mobile network, activate eSIMs, issue phone numbers, charge customers, verify identities, or access regulated carrier services.

## Quick start on Kali Linux

Download and extract the provided ZIP into `~/NAYVELO`, then initialize a private local Git repository:

```bash
cd ~/NAYVELO
git init -b main
git add .
git commit -m 'NAY-001 initial protected foundation'
```

You must configure your Git name/email if not already configured. Next, verify and run the demo:

```bash
cd ~/NAYVELO
python3 scripts/validate.py
python3 -m backend.nayvelo.server
# Visit http://127.0.0.1:8765
```

Default server binds to `127.0.0.1:8765`, for **local demo only**; do not expose this standard-library demo server publicly.

## Agent-assisted building

Requires `git`, an authenticated Codex CLI (`codex`) and, to create PRs, `gh` authenticated to GitHub. Read `AGENTS.md` and `engineering/RELEASE_GATES.md` before enabling automation.

```bash
python3 scripts/agent_build.py              # safe dry run, shows next task
python3 scripts/agent_build.py --execute    # generate code on a feature branch; run gates
python3 scripts/agent_build.py --execute --commit   # also commit verified changes locally
python3 scripts/agent_build.py --execute --commit --push --draft-pr  # publish DRAFT PR only
```

Requires a clean initialized Git repository with at least one commit and a `main` or `develop` branch. The agent does **one task per run** and does **not** merge, deploy, or turn on telecom capabilities. Configure manual or scheduled executions from a **secure isolated runner** only after authenticating locally and confirming the agent's permissions and costs. No secrets belong in the repository.

Codex supports `codex exec` with `--sandbox workspace-write`. This uses the configured Codex provider/account, potentially incurring usage costs. It is not offline inference.

## Flutter mobile app

The repository contains Flutter source files but not SDK-generated Android/iOS folders. With Flutter installed:

```bash
bash scripts/bootstrap_flutter.sh
cd apps/customer_app
flutter run
```

## Initial deliverables

- Read-only local mock API with **fail-closed telecom/payment endpoints**.
- Responsive web experience, NAYVELO brand theme, plan concept cards and a device-readiness checklist.
- Flutter Android/iOS source and widget tests.
- Agent task queue, git branch automation, test gates and read-only CI checks.
- Regulatory release boundaries documented in `engineering/RELEASE_GATES.md`.

## GitHub repository

No existing GitHub repository was found via the connected account at template creation time. Once you create a **private** repo using `gh auth login` then `gh repo create NAYVELO --private --source=. --remote=origin --push`, pushes and draft PR creation can be enabled. Do not treat a repo creation or a local archive as a network launch.

## Developer safeguards

No real NIN, SIM, customer phone numbers, payment credentials, eSIM activation codes, bank data or carrier secrets in tests, logs, public repositories or AI prompts.

## Optional autonomous nightly execution (opt in on your computer)

The prepared `scripts/autopilot_once.sh` checks for open pull requests, fast-forwards `main`, and creates **at most one new draft PR** using an authenticated local Codex CLI. It never merges, deploys, changes regulations or issues real SIMs. It will pause for the review gate. Run it on a dedicated low-privilege development account/runner, not your primary workstation with production secrets. The script runs the agent, which may incur API/subscription usage and can execute sandboxed code; inspect it before scheduling.

For example, after installing GitHub CLI, logging into GitHub, authenticating Codex and verifying a manual run, add this crontab entry with your own actual path (the example below assumes `/home/ahmadib/NAYVELO`):

```cron
15 2 * * * /bin/bash /home/ahmadib/NAYVELO/scripts/autopilot_once.sh >> /home/ahmadib/nayvelo-autopilot.log 2>&1
```

This job runs at **02:15 local machine time**, while the machine is running. It is a suggested schedule, **not configured by this package**. No Codex job is run in GitHub Actions, and no agent credentials are sent into pull-request CI jobs.
