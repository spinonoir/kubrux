# Contributing to kubrux

Thank you for your interest in contributing to kubrux! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- tmux installed
- `uv` for package management (recommended)

### Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/kubrux.git
   cd kubrux
   ```

2. **Install in development mode**:
   ```bash
   uv pip install -e .
   ```

3. **Verify installation**:
   ```bash
   kubrux --version
   ```

### Keeping Completions in Sync

When adding or changing CLI arguments in `kubrux.py`:

1. **shtab (auto-generated)**: Completions from `kubrux --print-completion {bash,zsh}` stay in sync automatically—no changes needed.

2. **Static files** (if using `completions/_kubrux` or `completions/kubrux.bash`): Update both files manually to add new flags. The static files include custom logic for `--host` (SSH) and `--session` (tmux) that shtab does not generate.

3. **Regenerate shtab outputs** (optional): `make completions` writes `completions/kubrux-shtab.bash` and `completions/_kubrux-shtab` for reference.

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and well-documented
- Add docstrings to classes and functions

## Testing

Before submitting changes:

1. **Test your changes**:
   ```bash
   # Test with a simple scene
   kubrux simple.scene --local
   ```

2. **Test multi-actor scenes**:
   ```bash
   kubrux tcp_handshake.scene
   ```

3. **Verify tmux session**:
   ```bash
   tmux attach -t kubrux
   ```

## Submitting Changes

1. **Create a branch** for your changes
2. **Make your changes** following the code style
3. **Test thoroughly** with various scene files
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## Areas for Contribution

- Bug fixes
- New directives or features
- Documentation improvements
- Example scenes
- Performance optimizations
- Error handling improvements

## Reporting Issues

When reporting issues, please include:

- kubrux version (`kubrux --version`)
- Python version (`python3 --version`)
- tmux version (`tmux -V`)
- Scene file that reproduces the issue
- Expected vs. actual behavior
- Error messages (if any)

## Questions?

Feel free to open an issue for questions or discussions about contributions.
