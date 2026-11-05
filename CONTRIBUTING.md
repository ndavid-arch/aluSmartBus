# Contributing to ALU SmartBus

These rules keep the work organised and every change traceable to a requirement.

## 1. Workflow

1. **Pick an issue** from the current sprint on the project board and move it to **In progress**.
2. **Create a branch** from `main`, named after the issue:
   ```
   feature/12-driver-starts-journey
   fix/27-eta-not-updating
   docs/5-update-readme
   ```
3. **Commit in small steps** (see the commit format below).
4. **Open a pull request** into `main` and fill in the template. Link the issue with `Closes #12`.
5. **Review** the pull request against the Definition of Done, then merge.
6. The issue closes automatically and moves to **Done**.

`main` should always run. Never commit straight to `main`.

## 2. Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary in the present tense>
```

| Type | Use for |
|---|---|
| `feat` | a new feature |
| `fix` | a bug fix |
| `test` | adding or changing tests |
| `docs` | documentation only |
| `refactor` | code change with no change in behaviour |
| `chore` | set-up, dependencies, configuration |

Examples:
```
feat: add endpoint to start a journey
fix: stop ETA showing negative minutes
test: cover duplicate QR scan on the same journey
```

## 3. Definition of Done

A user story is **Done** only when all of these are true:

- [ ] All acceptance criteria in the issue are met.
- [ ] Unit tests cover the new logic, and all tests pass (`pytest`).
- [ ] New API endpoints appear correctly in the FastAPI docs (`/docs`).
- [ ] The code passes the linter (Ruff / ESLint) with no errors.
- [ ] The feature works on a phone browser as well as a laptop.
- [ ] The pull request has been reviewed and merged into `main`.
- [ ] The traceability matrix lists the requirement, its test and the result.
- [ ] Any change to requirements or design is reflected in `docs/`.

## 4. Coding standards

- **Python:** follow PEP 8 and format with Ruff. Comment each function with a short docstring saying what it does.
- **JavaScript:** format with Prettier and lint with ESLint. Name components in PascalCase.
- **Secrets:** never commit passwords, keys or `.env` files. Use `.env.example` to show which settings are needed.

## 5. Testing

| Level | What | Tool |
|---|---|---|
| Unit (white-box) | Business logic such as ETA calculation and the boarding window | pytest |
| API (black-box) | Each endpoint against the acceptance criteria and boundary values | pytest + HTTPX test client |
| Integration | Location update reaching the student map | pytest + WebSocket test client |
| Manual | Phone tests with real drivers and students | test log in `docs/` |
