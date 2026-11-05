"""Create the repo description, labels, sprint milestones, backlog issues and project board on GitHub.

Run once from the repository root, after `gh auth login`:
    python scripts/setup_github.py
Needs the GitHub CLI (gh). In GitHub Codespaces it is already installed and logged in.
"""
import json
import subprocess
import sys

from backlog import ISSUES, LABELS, MILESTONES

DESCRIPTION = ("Real-time bus tracking and QR boarding for the ALU Rebero-ALU shuttle. "
               "FastAPI + PostgreSQL + React. ALU Intro to Software Engineering project.")
TOPICS = ["fastapi", "python", "react", "postgresql", "websockets", "bus-tracking", "scrum", "alu"]
PROJECT_TITLE = "ALU SmartBus Board"


def gh(*args, check=True):
    """Run a gh command and return its output text."""
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def repo_name():
    """Return owner/repo for the current folder."""
    return gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")


def setup_repo(repo):
    """Set the description and topics."""
    gh("repo", "edit", repo, "--description", DESCRIPTION,
       *[a for t in TOPICS for a in ("--add-topic", t)])
    print("✓ description and topics")


def setup_labels(repo):
    """Create or update every label."""
    for name, colour, desc in LABELS:
        gh("label", "create", name, "--repo", repo, "--color", colour, "--description", desc, "--force")
    print(f"✓ {len(LABELS)} labels")


def setup_milestones(repo):
    """Create the sprint milestones that do not exist yet."""
    existing = {m["title"] for m in json.loads(gh("api", f"repos/{repo}/milestones?state=all&per_page=100") or "[]")}
    for title, desc in MILESTONES:
        if title not in existing:
            gh("api", f"repos/{repo}/milestones", "-f", f"title={title}", "-f", f"description={desc}")
    print(f"✓ {len(MILESTONES)} milestones")


def setup_issues(repo):
    """Create each backlog issue unless one with the same title exists; return the issue URLs."""
    existing = {i["title"] for i in json.loads(gh("issue", "list", "--repo", repo, "--state", "all",
                                                  "--limit", "500", "--json", "title"))}
    urls = []
    for title, milestone, labels, body in ISSUES:
        if title in existing:
            continue
        url = gh("issue", "create", "--repo", repo, "--title", title, "--body", body,
                 "--milestone", milestone, *[a for lab in labels for a in ("--label", lab)])
        urls.append(url)
        print(f"  + {title}")
    print(f"✓ {len(urls)} new issues ({len(ISSUES) - len(urls)} already existed)")
    return urls


def setup_project(repo, urls):
    """Create the project board and add the issues (needs the 'project' scope)."""
    owner = repo.split("/")[0]
    try:
        out = gh("project", "create", "--owner", owner, "--title", PROJECT_TITLE, "--format", "json")
        number = json.loads(out)["number"]
        for url in urls:
            gh("project", "item-add", str(number), "--owner", owner, "--url", url)
        gh("project", "link", str(number), "--owner", owner, "--repo", repo, check=False)
        print(f"✓ project board '{PROJECT_TITLE}' with {len(urls)} items")
    except RuntimeError as e:
        print("! project board not created:", e)
        print("  Run:  gh auth refresh -s project   then run this script again,")
        print("  or create the board on GitHub (Projects → New project → Board) and add the issues.")


def main():
    """Run every set-up step in order."""
    try:
        gh("--version")
    except FileNotFoundError:
        sys.exit("The GitHub CLI (gh) is not installed: https://cli.github.com")
    repo = repo_name()
    print(f"Setting up {repo}\n")
    setup_repo(repo)
    setup_labels(repo)
    setup_milestones(repo)
    urls = setup_issues(repo)
    setup_project(repo, urls)
    print("\nDone.")


if __name__ == "__main__":
    main()
