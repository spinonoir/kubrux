# API Documentation

kubrux can be used both as a command-line tool and as a Python library.

## Command Line Interface

### Main Entry Point

```python
from kubrux import main

exit(main())
```

### Command Line Arguments

The `main()` function uses `argparse` to parse command-line arguments:

- `scene_file` (required): Path to the scene file
- `--host`: Default SSH host (for legacy single-actor scenes when no @actor defined)
- `--dir`, `-d`: Default working directory (for legacy single-actor scenes when no @actor defined)
- `--script`, `-s`: Default script recording filename (for legacy single-actor scenes when no @actor defined)
- `--session`: tmux session name (default: "kubrux")
- `--local`: Run locally without SSH (for legacy single-actor scenes when no @actor defined)
- `--help-scene`: Show detailed scene file format
- `--version`: Show version number

## Python API

### Kubrux Class

The main class for orchestrating terminal scenes.

```python
from kubrux import Kubrux

director = Kubrux(session_name="my_session")
```

#### Constructor

```python
Kubrux(session_name: str = "kubrux")
```

Creates a new kubrux director instance.

- **session_name**: Name for the tmux session (default: "kubrux")
- **Note**: Any existing session with the same name will be killed

#### Methods

##### `add_actor(config: ActorConfig)`

Add an actor to the cast and prepare their stage (pane).

```python
config = ActorConfig(
    name="server",
    host="host353",
    working_dir="~/lab",
    script_file="server.log"
)
director.add_actor(config)
```

##### `direct(scene_file: Path, default_host: str = None, default_dir: str = None, default_script: str = None, default_local: bool = False)`

Direct a scene from a scene file.

```python
from pathlib import Path

director.direct(
    Path("my_scene.scene"),
    default_host="host353",
    default_dir="~/lab"
)
```

**Parameters:**
- `scene_file`: Path to the scene file
- `default_host`: Default SSH host (for legacy single-actor scenes when no @actor defined)
- `default_dir`: Default working directory (for legacy single-actor scenes when no @actor defined)
- `default_script`: Default script recording filename (for legacy single-actor scenes when no @actor defined)
- `default_local`: Run locally without SSH (for legacy single-actor scenes when no @actor defined)

##### `deliver_line(line: str, actor: str = None)`

Actor types and delivers a line (command).

```python
director.deliver_line("ls -la", actor="server")
```

##### `type_without_enter(text: str, actor: str = None)`

Actor types but holds (no Enter).

```python
director.type_without_enter("echo 'Hello'", actor="client")
director.send_enter(actor="client")
```

##### `send_instant(command: str, actor: str = None)`

Instant delivery, no typing effect.

```python
director.send_instant("clear", actor="server")
```

##### `send_enter(actor: str = None)`

Just press Enter.

```python
director.send_enter(actor="client")
```

##### `ctrl_c(actor: str = None)`

Send Ctrl+C.

```python
director.ctrl_c(actor="server")
```

##### `ctrl_d(actor: str = None)`

Send Ctrl+D (EOF).

```python
director.ctrl_d(actor="client")
```

##### `ctrl_z(actor: str = None)`

Send Ctrl+Z (suspend).

```python
director.ctrl_z(actor="process")
```

##### `send_key(key: str, actor: str = None)`

Send a special key.

```python
director.send_key("Tab", actor="client")
director.send_key("Up", actor="client")
```

##### `clear_stage(actor: str = None)`

Clear the screen.

```python
director.clear_stage(actor="server")
```

##### `wrap()`

Stop all script recordings.

```python
director.wrap()
```

### ActorConfig Class

Configuration for a single actor.

```python
from kubrux import ActorConfig

config = ActorConfig(
    name="server",
    host="host353",
    working_dir="~/lab",
    script_file="server.log",
    is_local=False
)
```

#### Fields

- `name` (str): Actor identifier
- `host` (Optional[str]): SSH host to connect to
- `working_dir` (Optional[str]): Working directory on the host
- `script_file` (Optional[str]): Script recording filename
- `is_local` (bool): Run locally without SSH
- `pane` (Optional[libtmux.Pane]): The tmux pane (set automatically)

## Example: Programmatic Usage

```python
from kubrux import Kubrux, ActorConfig
from pathlib import Path
import time

# Create director
director = Kubrux(session_name="demo")

# Add actors
server_config = ActorConfig(
    name="server",
    host="host353",
    working_dir="~/lab",
    script_file="server.log"
)
director.add_actor(server_config)

client_config = ActorConfig(
    name="client",
    host="host353",
    working_dir="~/lab",
    script_file="client.log"
)
director.add_actor(client_config)

# Direct the scene
director.deliver_line("nc -l 8080", actor="server")
time.sleep(1)
director.deliver_line("nc localhost 8080", actor="client")
time.sleep(1)
director.type_without_enter("Hello!", actor="client")
director.send_enter(actor="client")
time.sleep(2)
director.ctrl_c(actor="client")
director.ctrl_c(actor="server")

# Wrap up
director.wrap()
print("Scene complete!")
```

## Example: Loading Scene File Programmatically

```python
from kubrux import Kubrux
from pathlib import Path

director = Kubrux(session_name="my_scene")
director.direct(
    Path("my_scene.scene"),
    default_host="host353",
    default_dir="~/lab"
)
director.wrap()
```

## Timing Control

You can adjust timing parameters:

```python
director = Kubrux()

# Set typing speed (seconds per character)
director.typing_delay = 0.1  # Slower

# Set post-line pause (seconds after command)
director.line_pause = 2.0  # Longer pause
```

## Layout Control

Set the layout before adding actors:

```python
director = Kubrux()
director.layout = "horizontal"  # or "vertical"

# Now add actors - they'll be arranged horizontally
director.add_actor(server_config)
director.add_actor(client_config)
```

## Accessing tmux Panes

You can access the underlying tmux panes:

```python
director = Kubrux()
director.add_actor(server_config)

# Get the pane for an actor
pane = director._get_pane("server")

# Access libtmux pane methods directly
pane.capture_pane()  # Get pane contents
pane.send_keys("custom command", enter=True)
```

## Error Handling

```python
from kubrux import Kubrux

try:
    director = Kubrux()
    director.direct(Path("scene.scene"))
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    director.wrap()
```

## Version

```python
from kubrux import __version__

print(__version__)  # "1.0.0"
```
