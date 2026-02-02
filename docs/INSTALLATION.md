# Installation Guide

This guide covers installing kubrux and its dependencies.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **tmux**: Version 2.0 or higher
- **SSH**: For remote execution (optional, only needed if using `--host`)

### Check Your Environment

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check tmux version
tmux -V  # Should be 2.0+

# Check if SSH is available (optional)
ssh -V
```

## Installing tmux

### macOS

```bash
# Using Homebrew
brew install tmux
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tmux
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install tmux
```

## Installing kubrux

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

#### Step 1: Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

#### Step 2: Install kubrux

From the kubrux directory:

```bash
# Install in development mode (editable)
uv pip install -e .

# Or install as a regular package
uv pip install .
```

This will automatically install `libtmux` and other dependencies.

### Using pip (Alternative)

If you prefer using pip directly:

```bash
# Install dependencies
pip install libtmux

# Install kubrux (if it's a package)
pip install .

# Or run directly without installation
python3 kubrux.py scene.scene
```

### Using pipx (For CLI Tools)

If you want to install kubrux as a standalone CLI tool:

```bash
# Install pipx if needed
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install kubrux
pipx install .
```

## Verifying Installation

After installation, verify kubrux is working:

```bash
# Check if kubrux is in PATH
kubrux --version

# Should output: kubrux 1.0.0

# Test with help
kubrux --help

# View scene file format help
kubrux --help-scene
```

## Shell Tab Completion

kubrux supports two completion methods:

### Option A: Always-in-sync (recommended)

Install kubrux, then add to your shell config. Completions stay in sync with the installed version automatically:

```bash
uv tool install .
# Or: pipx install .
```

**Zsh** – add to `~/.zshrc`:
```bash
source <(kubrux --print-completion zsh)
```

**Bash** – add to `~/.bashrc`:
```bash
source <(kubrux --print-completion bash)
```

Restart your shell (or `source ~/.zshrc` / `source ~/.bashrc`).

### Option B: Static completion files

kubrux ships completion scripts with custom logic for SSH hosts and tmux sessions in `completions/`.

**Zsh** – add to `~/.zshrc` (adjust the path to your clone):
```bash
fpath=(/path/to/kubrux/completions $fpath)
autoload -Uz compinit && compinit
```

**Bash** – add to `~/.bashrc` (adjust the path):
```bash
source /path/to/kubrux/completions/kubrux.bash
```

After upgrading, restart your shell to pick up changes.

## Development Setup

For development, install in editable mode with development dependencies:

```bash
# Using uv
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

## Troubleshooting

### tmux Not Found

If you get an error that tmux is not found:

1. Verify tmux is installed: `tmux -V`
2. Check if tmux is in your PATH: `which tmux`
3. On macOS, you may need to add Homebrew's bin directory to PATH:
   ```bash
   echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### libtmux Installation Issues

If `libtmux` fails to install:

```bash
# Try upgrading pip first
uv pip install --upgrade pip

# Or with pip
pip install --upgrade pip setuptools wheel
pip install libtmux
```

### Permission Errors

If you encounter permission errors:

```bash
# Use --user flag with pip
pip install --user libtmux

# Or use a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv pip install -e .
```

### SSH Connection Issues

If using remote hosts, ensure:

1. SSH keys are set up for passwordless authentication
2. The remote host is accessible: `ssh hostname`
3. The working directory exists on the remote host

## Next Steps

After installation, see:
- [Scene File Format](SCENE_FORMAT.md) - Learn how to write scene files
- [Examples](EXAMPLES.md) - See example scenes
- [API Documentation](API.md) - Use kubrux programmatically
