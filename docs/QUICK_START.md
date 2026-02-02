# Quick Start Guide

Get up and running with kubrux in 5 minutes.

## Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install kubrux
cd /path/to/kubrux
uv pip install -e .
```

## Your First Scene

Create a file called `hello.scene`:

```bash
## hello.scene
@actor client --local --dir ~

client: echo "Hello, kubrux!"
client: pwd
client: ls -la
```

Run it:

```bash
kubrux hello.scene
```

Watch it in another terminal:

```bash
tmux attach -t kubrux
```

## Two-Actor Scene

Create `chat.scene`:

```bash
@actor alice --local --dir ~
@actor bob --local --dir ~
@layout vertical

alice: echo "Hello from Alice!"
@pause 1
bob: echo "Hello from Bob!"
@pause 1
alice: echo "Nice to meet you!"
```

Run it:

```bash
kubrux chat.scene
```

## Next Steps

- Read the [Scene File Format](SCENE_FORMAT.md) for all available directives
- Check out [Examples](EXAMPLES.md) for more complex scenarios
- See [Installation Guide](INSTALLATION.md) for detailed setup
- Review [API Documentation](API.md) for programmatic usage

## Common Commands

```bash
# Run a scene (actors defined in scene file)
kubrux scene.scene

# Legacy: Run with CLI args (if no @actor in scene file)
kubrux scene.scene --host hostname --dir ~/path

# Custom session name
kubrux scene.scene --session my_session

# View scene format help
kubrux --help-scene
```

## Troubleshooting

**tmux not found:**
```bash
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt-get install tmux
```

**Can't see the performance:**
```bash
# Attach to the tmux session
tmux attach -t kubrux

# Or list sessions
tmux ls
```

**SSH connection issues:**
- Ensure SSH keys are set up for passwordless authentication
- Test SSH connection manually: `ssh hostname`
- Verify the working directory exists on the remote host
