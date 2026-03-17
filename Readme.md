# tsk

A minimal, aesthetic task manager for the terminal.

```
  Tasks  3 open / 5 total

  ID   PRIORITY    TASK                          TAG        DUE
 ──── ─────────── ───────────────────────────── ─────────  ─────────────
  1   ● high       Submit IEEE paper draft        research   in 1d
  2   ● medium     Review pull requests           work       —
  3   ● low        Read Designing Data-Int. Apps  reading    2026-04-01
```

---

## Features

- **Priorities** — high / medium / low, colour-coded at a glance
- **Due dates** — overdue, due-today, and upcoming warnings built in
- **Tags** — group tasks by any category you like
- **Edit** — update any field of an existing task without re-creating it
- **Stats** — progress bar + per-priority breakdown
- **Clean storage** — a single JSON file in `~/.config/tsk/tasks.json`; easy to back up or sync

---

## Requirements

- Python 3.10 or higher

---

## Installation

After installing, the `tsk` command is available globally.

### Option 1 — from source

```bash
git clone https://github.com/yourname/getShiDone.git
cd getShiDone
pip install .
```

### Option 2 — no install (run directly)

```bash
git clone https://github.com/yourname/getShiDone.git
cd getShiDone
pip install -r requirements.txt
python todo.py
```

You can alias it for convenience:

```bash
# ~/.bashrc or ~/.zshrc
alias tsk="python /path/to/tsk/todo.py"
```

---

## Usage

```
tsk [COMMAND] [OPTIONS]
```

Running `tsk` with no arguments shows your open task list.

---

### Commands

#### `add` — Add a task

```bash
tsk add "Task description"
tsk add "Task description" -p high
tsk add "Task description" -p medium -d 2026-04-15
tsk add "Task description" -p low -d 2026-04-15 -t work
```

| Flag | Short | Description |
|------|-------|-------------|
| `--priority` | `-p` | `high`, `medium` (default), or `low` |
| `--due` | `-d` | Due date in `YYYY-MM-DD` format |
| `--tag` | `-t` | Any string — used to group and filter tasks |

---

#### `list` — List tasks

```bash
tsk list          # open tasks only (same as just running tsk)
tsk list -a       # include completed tasks
tsk list -t work  # filter by tag
tsk list -p high  # filter by priority
```

| Flag | Short | Description |
|------|-------|-------------|
| `--all` | `-a` | Show completed tasks too |
| `--tag` | `-t` | Filter by tag |
| `--priority` | `-p` | Filter by priority |

---

#### `done` — Complete a task

```bash
tsk done 3
```

---

#### `undone` — Reopen a task

```bash
tsk undone 3
```

---

#### `edit` — Update a task

```bash
tsk edit 3 --task "New description"
tsk edit 3 -p high
tsk edit 3 -d 2026-05-01
tsk edit 3 -t personal
```

Any combination of flags can be passed together. Only the specified fields are updated.

---

#### `delete` — Remove a task

```bash
tsk delete 3           # asks for confirmation
tsk delete 3 --force   # skips confirmation
```

---

#### `clear` — Remove all completed tasks

```bash
tsk clear           # asks for confirmation
tsk clear --force   # skips confirmation
```

---

#### `stats` — Task summary

```bash
tsk stats
```

```
  Stats

  ████████████████░░░░░░░░░░░░  57% complete

  total     7
  done      4
  pending   3
  overdue   1

  open by priority
  ● high    ██ 2
  ● medium  █ 1
  ● low       none
```

---

## Data

Tasks are stored in a plain JSON file:

```
~/.config/tsk/tasks.json
```

You can override the location with the `TSK_DATA_DIR` environment variable:

```bash
export TSK_DATA_DIR="$HOME/Dropbox/tsk"
```

This makes it easy to sync tasks across machines via Dropbox, iCloud, or any other file sync tool.

---

## Uninstall

```bash
pip uninstall tsk-cli
```

To also remove your task data:

```bash
rm -rf ~/.config/tsk
```

---

## License

MIT