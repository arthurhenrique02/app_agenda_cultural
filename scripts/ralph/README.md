# Ralph Loop (Local Project Setup)

This folder contains a local Ralph loop setup inspired by `snarktank/ralph`.

## Files

- `ralph.sh`: loop runner
- `CLAUDE.md`: iteration instructions for Claude Code
- `prompt.md`: iteration instructions for Amp
- `prd.json`: current story backlog for Ralph
- `prd.json.example`: reference format
- `progress.txt`: append-only iteration log
- `archive/`: previous runs archived automatically by branch name

## Usage

From project root:

```bash
./scripts/ralph/ralph.sh --tool claude 10
```

Or with Amp:

```bash
./scripts/ralph/ralph.sh --tool amp 10
```

## Dev Container Workflow

1. Open the repository in VS Code.
2. Run `Dev Containers: Rebuild and Reopen in Container`.
3. Authenticate your AI tool inside the container (`claude` or `amp`).
4. Update `scripts/ralph/prd.json` with your current stories.
5. Run `./scripts/ralph/ralph.sh --tool claude 10`.

## First Run

1. Update `scripts/ralph/prd.json` with your feature stories.
2. Ensure `jq` is installed.
3. Ensure the selected tool CLI is installed and authenticated (`claude` or `amp`).
4. Run `./scripts/ralph/ralph.sh --tool claude`.

## Notes

- The script archives prior runs when `branchName` changes.
- The loop exits early when output contains `<promise>COMPLETE</promise>`.
- Keep stories small so each one can finish in a single iteration.
