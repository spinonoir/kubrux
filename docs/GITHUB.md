# Publishing kubrux to GitHub

## Initial Setup

### 1. Create a new repository on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Create a repository named `kubrux` (or your preferred name)
3. Do **not** initialize with a README, .gitignore, or license (this project already has them)

### 2. Initialize Git (if not already done)

```bash
cd /path/to/kubrux
git init
```

### 3. Add the remote and push

```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/kubrux.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Upgrading After Pushing

When you make changes locally:

```bash
git add .
git commit -m "Describe your changes"
git push
```

Then upgrade the installed tool:

```bash
cd /path/to/kubrux
git pull
uv tool install --force .
```

Completions stay in sync if you use `source <(kubrux --print-completion zsh)` in your shell config. If you use the static completion files, restart your shell after upgrading.
