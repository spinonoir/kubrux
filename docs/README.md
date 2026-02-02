# kubrux

**Deterministic multi-terminal scene direction using tmux**

kubrux is a CLI tool for staging deterministic, multi-terminal interactions using tmux. It takes an external script—written as one or more `*.scene` files—and directs terminal "actors" to perform their roles exactly as specified.

The name is a portmanteau of **Kubrick** and **Unix**: a nod to Stanley Kubrick's reputation for meticulous, scene-by-scene control, and to the Unix/tmux environment kubrux operates in. Like a film director, kubrux does not invent the story; it interprets and executes it with precision.

## Features

- **Scene-based scripting**: Write terminal interactions as scene files
- **Multi-actor support**: Coordinate multiple terminals simultaneously
- **Remote execution**: SSH into different hosts for distributed scenarios
- **Script recording**: Automatically record terminal sessions
- **Precise timing**: Control typing speed, pauses, and delays
- **Layout control**: Arrange panes horizontally or vertically
- **Deterministic**: Reproducible terminal interactions every time

## Quick Start

### Installation

kubrux requires Python 3.8+ and tmux. Install using `uv`:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install kubrux
uv pip install -e .

# Or install from a directory
cd /path/to/kubrux
uv pip install -e .
```

### Basic Usage

**Single-actor scene (recommended):**
```bash
# Define actor in scene file, then run:
kubrux demo.scene
```

**Multi-actor scene:**
```bash
kubrux client_server.scene
```

**Legacy single-actor mode (using CLI args):**
```bash
kubrux demo.scene --host host353 --dir ~/lab
```

**Watch the performance:**
```bash
tmux attach -t kubrux
```

## Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Scene File Format](SCENE_FORMAT.md) - Complete reference for writing scene files
- [API Documentation](API.md) - Python API reference
- [Examples](EXAMPLES.md) - Example scenes and use cases

## Example Scenes

**Single-actor scene:**
```bash
@actor client --host host353 --dir ~/lab --script client.log

client: # Show where we are
client: pwd
client: ls -la
client: echo "Scene complete"
```

**Multi-actor scene:**
```bash
@actor server --host host353 --dir ~/lab --script server.log
@actor client --host host353 --dir ~/lab --script client.log

server: # Start the server
server: nc -l 8080
@pause 1
client: # Connect to server  
client: nc localhost 8080
client: @type Hello!
client: @enter
@pause 2
client: @ctrl-c
server: @ctrl-c
```

## Command Line Options

```
usage: kubrux [-h] [--host HOST] [--dir DIR] [--script SCRIPT] 
              [--session SESSION] [--local] [--help-scene] [--version]
              scene_file

positional arguments:
  scene_file            Scene file (*.scene) containing the script

options:
  -h, --help            show this help message and exit
  --host HOST           Default SSH host (legacy: when no @actor in scene file)
  -d, --dir DIR         Default working directory (legacy: when no @actor in scene file)
  -s, --script SCRIPT   Default script recording filename (legacy: when no @actor in scene file)
  --session SESSION     tmux session name (default: kubrux)
  --local               Run locally, no SSH (legacy: when no @actor in scene file)
  --help-scene          Show detailed scene file format
  --version             show program's version number and exit
```

## Shell Tab Completion

Completion scripts are included in `completions/`:

- **Zsh**: add `completions/` to your `fpath` and run `compinit`
- **Bash**: `source completions/kubrux.bash` (requires `bash-completion` for best results)

See `docs/INSTALLATION.md` for copy/paste setup snippets.

## Requirements

- Python 3.8 or higher
- tmux (installed and in PATH)
- libtmux (Python package, installed automatically)

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.
