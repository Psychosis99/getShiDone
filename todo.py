#!/usr/bin/env python3
"""
tsk — A minimal, aesthetic CLI task manager.
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

# ── Config ────────────────────────────────────────────────────────────────────

APP_DIR  = Path(os.getenv("TSK_DATA_DIR", Path.home() / ".config" / "tsk"))
DATA_FILE = APP_DIR / "tasks.json"

app     = typer.Typer(invoke_without_command=True, add_completion=False)
console = Console()

# ── Palette ───────────────────────────────────────────────────────────────────

C = {
    "high"   : "bold red",
    "medium" : "yellow",
    "low"    : "cyan",
    "done"   : "bright_black",
    "accent" : "bright_white",
    "muted"  : "bright_black",
    "ok"     : "green",
    "warn"   : "dark_orange",
    "err"    : "red",
    "id"     : "bright_black",
    "tag"    : "magenta",
}

PRIORITY_TAG = {
    "high"  : "[bold red]● high  [/]",
    "medium": "[yellow]● medium[/]",
    "low"   : "[cyan]● low   [/]",
}

# ── Storage ───────────────────────────────────────────────────────────────────

def load() -> list[dict]:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save(tasks: list[dict]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def next_id(tasks: list[dict]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1

def find(tasks: list[dict], task_id: int) -> Optional[dict]:
    return next((t for t in tasks if t["id"] == task_id), None)

# ── Due-date helpers ──────────────────────────────────────────────────────────

def due_display(due_str: Optional[str]) -> tuple[str, str]:
    """Returns (label, rich_style) based on how urgent the due date is."""
    if not due_str:
        return "—", C["muted"]
    d     = date.fromisoformat(due_str)
    today = date.today()
    delta = (d - today).days
    if delta < 0:
        return f"overdue {abs(delta)}d", C["err"]
    if delta == 0:
        return "due today", C["warn"]
    if delta <= 2:
        return f"in {delta}d", C["warn"]
    return due_str, C["muted"]

def parse_due(due: Optional[str]) -> Optional[str]:
    if due is None:
        return None
    try:
        date.fromisoformat(due)
        return due
    except ValueError:
        console.print(f"[{C['err']}]Due date must be YYYY-MM-DD.[/]")
        raise typer.Exit(1)

def parse_priority(p: str) -> str:
    if p not in ("high", "medium", "low"):
        console.print(f"[{C['err']}]Priority must be: high, medium, or low.[/]")
        raise typer.Exit(1)
    return p

# ── Commands ──────────────────────────────────────────────────────────────────

@app.callback()
def default(ctx: typer.Context):
    """tsk — a fast, minimal task manager for the terminal."""
    if ctx.invoked_subcommand is None:
        list_tasks(show_done=False, tag=None, priority=None)


@app.command("add")
def add_task(
    task    : str            = typer.Argument(...,                         help="Task description."),
    priority: str            = typer.Option("medium", "-p", "--priority", help="high / medium / low"),
    due     : Optional[str]  = typer.Option(None,     "-d", "--due",      help="Due date YYYY-MM-DD"),
    tag     : Optional[str]  = typer.Option(None,     "-t", "--tag",      help="Category tag"),
):
    """Add a new task."""
    priority = parse_priority(priority)
    due      = parse_due(due)
    tasks    = load()
    tid      = next_id(tasks)
    tasks.append({
        "id"      : tid,
        "task"    : task,
        "done"    : False,
        "priority": priority,
        "due"     : due,
        "tag"     : tag,
        "created" : datetime.now().isoformat(),
    })
    save(tasks)
    console.print(f"  [{C['ok']}]+[/] [{C['accent']}]{task}[/]  [{C['id']}]#{tid}[/]")


@app.command("list")
def list_tasks(
    show_done: bool          = typer.Option(False, "-a", "--all",      help="Include completed tasks."),
    tag      : Optional[str] = typer.Option(None,  "-t", "--tag",      help="Filter by tag."),
    priority : Optional[str] = typer.Option(None,  "-p", "--priority", help="Filter by priority."),
):
    """List tasks. Runs by default with no subcommand."""
    tasks = load()
    rows  = tasks if show_done else [t for t in tasks if not t["done"]]
    if tag:
        rows = [t for t in rows if t.get("tag") == tag]
    if priority:
        rows = [t for t in rows if t.get("priority") == priority]

    pending = sum(1 for t in tasks if not t["done"])
    total   = len(tasks)

    console.print()

    if not rows:
        console.print(f"  [{C['muted']}]No tasks. Add one:[/]  tsk add \"your task\"")
        console.print()
        return

    tbl = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style=f"bold {C['muted']}",
        padding=(0, 1),
        show_edge=False,
        show_footer=False,
    )
    tbl.add_column("ID",       style=C["id"],    width=5, no_wrap=True)
    tbl.add_column("PRIORITY", width=10,          no_wrap=True)
    tbl.add_column("TASK",     min_width=28)
    tbl.add_column("TAG",      style=C["tag"],   width=13, no_wrap=True)
    tbl.add_column("DUE",      width=14,          no_wrap=True)
    tbl.add_column("",         width=5,           no_wrap=True)  # status pill

    for t in rows:
        done = t["done"]
        due_label, due_style = due_display(t.get("due"))

        task_text = Text(t["task"])
        if done:
            task_text.stylize(C["done"])
            task_text.stylize("strike")

        status_pill = f"[{C['ok']}]done[/]" if done else ""

        tbl.add_row(
            str(t["id"]),
            PRIORITY_TAG.get(t.get("priority", "medium"), ""),
            task_text,
            t.get("tag") or "—",
            f"[{due_style}]{due_label}[/]",
            status_pill,
        )

    header = Text()
    header.append("  Tasks", style=f"bold {C['accent']}")
    header.append(f"  {pending} open", style=C["muted"])
    header.append(" / ", style=C["muted"])
    header.append(f"{total} total", style=C["muted"])
    console.print(header)
    console.print()
    console.print(tbl)
    console.print()


@app.command("done")
def mark_done(task_id: int = typer.Argument(..., help="Task ID.")):
    """Mark a task as complete."""
    tasks = load()
    t     = find(tasks, task_id)
    if not t:
        console.print(f"  [{C['err']}]No task #{task_id}.[/]")
        raise typer.Exit(1)
    t["done"]         = True
    t["completed_at"] = datetime.now().isoformat()
    save(tasks)
    console.print(f"  [{C['ok']}]done[/]  [{C['done']}]{t['task']}[/]  [{C['id']}]#{task_id}[/]")


@app.command("undone")
def mark_undone(task_id: int = typer.Argument(..., help="Task ID.")):
    """Reopen a completed task."""
    tasks = load()
    t     = find(tasks, task_id)
    if not t:
        console.print(f"  [{C['err']}]No task #{task_id}.[/]")
        raise typer.Exit(1)
    t["done"] = False
    t.pop("completed_at", None)
    save(tasks)
    console.print(f"  [{C['accent']}]reopened[/]  {t['task']}  [{C['id']}]#{task_id}[/]")


@app.command("edit")
def edit_task(
    task_id : int            = typer.Argument(...,                         help="Task ID."),
    task    : Optional[str]  = typer.Option(None, "--task",               help="New description."),
    priority: Optional[str]  = typer.Option(None, "-p", "--priority",     help="New priority."),
    due     : Optional[str]  = typer.Option(None, "-d", "--due",          help="New due date YYYY-MM-DD."),
    tag     : Optional[str]  = typer.Option(None, "-t", "--tag",          help="New tag."),
):
    """Edit a task's fields."""
    tasks = load()
    t     = find(tasks, task_id)
    if not t:
        console.print(f"  [{C['err']}]No task #{task_id}.[/]")
        raise typer.Exit(1)
    if task:
        t["task"] = task
    if priority:
        t["priority"] = parse_priority(priority)
    if due:
        t["due"] = parse_due(due)
    if tag:
        t["tag"] = tag
    save(tasks)
    console.print(f"  [{C['accent']}]updated[/]  #{task_id}")


@app.command("delete")
def delete_task(
    task_id: int  = typer.Argument(...,                              help="Task ID."),
    force  : bool = typer.Option(False, "-f", "--force",            help="Skip confirmation."),
):
    """Delete a task permanently."""
    tasks = load()
    t     = find(tasks, task_id)
    if not t:
        console.print(f"  [{C['err']}]No task #{task_id}.[/]")
        raise typer.Exit(1)
    if not force:
        typer.confirm(f"Delete #{task_id}: \"{t['task']}\"?", abort=True)
    save([x for x in tasks if x["id"] != task_id])
    console.print(f"  [{C['muted']}]deleted #{task_id}[/]")


@app.command("clear")
def clear_done(force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation.")):
    """Remove all completed tasks."""
    tasks = load()
    done  = [t for t in tasks if t["done"]]
    if not done:
        console.print(f"  [{C['muted']}]Nothing to clear.[/]")
        return
    if not force:
        typer.confirm(f"Remove {len(done)} completed task(s)?", abort=True)
    save([t for t in tasks if not t["done"]])
    console.print(f"  [{C['muted']}]Cleared {len(done)} task(s).[/]")


@app.command("stats")
def stats():
    """Show a summary of your tasks."""
    tasks   = load()
    total   = len(tasks)
    done    = sum(1 for t in tasks if t["done"])
    pending = total - done
    today   = date.today()
    overdue = sum(
        1 for t in tasks
        if not t["done"] and t.get("due") and date.fromisoformat(t["due"]) < today
    )
    by_p = {p: sum(1 for t in tasks if not t["done"] and t.get("priority") == p)
            for p in ("high", "medium", "low")}

    pct = int((done / total) * 100) if total else 0
    bar_len   = 28
    filled    = int(bar_len * pct / 100)
    bar       = f"[{C['ok']}]{'█' * filled}[/][{C['muted']}]{'░' * (bar_len - filled)}[/]"

    console.print()
    console.print(f"  [bold {C['accent']}]Stats[/]")
    console.print()
    console.print(f"  {bar}  [bold]{pct}%[/] complete")
    console.print()
    console.print(f"  [{C['muted']}]total   [/]  {total}")
    console.print(f"  [{C['ok']}]done    [/]  {done}")
    console.print(f"  [{C['accent']}]pending [/]  {pending}")
    if overdue:
        console.print(f"  [{C['err']}]overdue [/]  {overdue}")
    console.print()
    console.print(f"  [{C['muted']}]open by priority[/]")
    for p, count in by_p.items():
        bar_p = "█" * count if count else f"[{C['muted']}]none[/]"
        console.print(f"  {PRIORITY_TAG[p]}  {bar_p} {count if count else ''}")
    console.print()


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()