# Scene File Format Reference

Scene files (`.scene`) are the scripts that kubrux executes. They define actors, their roles, and the sequence of commands and actions they perform.

## File Structure

Scene files are plain text files with the `.scene` extension. They consist of:

1. **Actor definitions** (at the top)
2. **Layout directives** (optional)
3. **Dialogue and directions** (the main script)

## Actor Definitions

### Single Actor Mode (Recommended)

For consistency, always define at least one actor with a name, even for single-actor scenes:

```
@actor client --host host353 --dir ~/lab --script client.log
```

Then use the actor name in dialogue lines:

```
client: pwd
client: ls -la
client: echo "Done"
```

**Benefits:**
- Consistent format across all scene files
- Clear actor identification
- Easy to convert to multi-actor scenes later

### Legacy Single Actor Mode

If no `@actor` directives are present, kubrux falls back to single-actor mode using command-line arguments (creates a "default" actor):

```bash
kubrux scene.scene --host hostname --dir ~/path
```

In this mode, commands can be written without actor prefixes, and they go to the default actor. However, **defining an actor name is recommended** for consistency.

### Multi-Actor Mode

Define multiple actors at the top of the scene file:

```
@actor NAME --host HOSTNAME --dir PATH [--script FILE] [--local]
```

**Parameters:**

- `NAME`: Actor identifier (used in dialogue lines)
- `--host HOSTNAME`: SSH host to connect to (optional)
- `--dir PATH`: Working directory on the host
- `--script FILE`: Start `script` recording to this file (optional)
- `--local`: Run locally without SSH (optional)

**Examples:**

```
# Single actor scene
@actor client --host host353 --dir ~/lab --script client.log

# Multi-actor scene
@actor server --host host353 --dir ~/lab --script server.log
@actor client --host host353 --dir ~/lab --script client.log

# Local actor
@actor local --local --dir ~/test
```

## Layout Directives

Control how panes are arranged:

```
@layout horizontal|vertical
```

- `vertical` (default): Panes split vertically (side by side)
- `horizontal`: Panes split horizontally (stacked)

**Example:**

```
@actor alice --host host1 --dir ~
@actor bob --host host2 --dir ~
@layout horizontal
```

## Dialogue Lines

Actors deliver lines (commands) using this format:

```
ACTOR_NAME: command
```

**Examples:**

```
server: nc -l 8080
client: curl http://localhost:8080
alice: echo "Hello, Bob!"
```

If no actor is specified, the command goes to the lead actor (first defined actor).

## Directives

Directives are special commands that control timing, input, and behavior.

### Timing Directives

#### `@pause N`

Hold for N seconds before continuing.

```
@pause 2.5
```

#### `@delay N`

Set typing speed (seconds per character). Default: 0.04s

```
@delay 0.1  # Slower typing
@delay 0.01 # Faster typing
```

#### `@wait N`

Set post-line pause (seconds after executing a command). Default: 1.0s

```
@wait 0.5  # Shorter pause after commands
@wait 2.0  # Longer pause after commands
```

### Input Directives

#### `@ctrl-c`

Send Ctrl+C (interrupt signal).

```
server: @ctrl-c
```

#### `@ctrl-d`

Send Ctrl+D (EOF signal).

```
client: @ctrl-d
```

#### `@ctrl-z`

Send Ctrl+Z (suspend signal).

```
process: @ctrl-z
```

#### `@key KEYNAME`

Send a special key. Common keys: `Up`, `Down`, `Left`, `Right`, `Tab`, `Escape`, `Enter`.

```
client: @key Tab      # Auto-complete
client: @key Up       # Command history
client: @key Escape   # Cancel
```

### Display Directives

#### `@clear`

Clear the screen.

```
server: @clear
```

### Text Input Directives

#### `@send TEXT`

Send text instantly (no typing effect, executes immediately).

```
client: @send ls -la
```

#### `@type TEXT`

Type text without pressing Enter (no execution).

```
client: @type echo "Hello"
client: @enter  # Now press Enter
```

#### `@enter`

Press Enter key.

```
client: @type ls -la
client: @enter
```

## Comments

### Director's Notes

Lines starting with `##` are director's notes (ignored by kubrux):

```
## This is a comment that won't be executed
## === ACT 1: SETUP ===
server: nc -l 8080
```

### Shell Comments

Lines starting with `#` (not `##`) are typed as shell comments (part of the performance):

```
server: # Starting the server
server: nc -l 8080
```

## Empty Lines

Empty lines are ignored and can be used for readability:

```
server: nc -l 8080

@pause 1

client: nc localhost 8080
```

## Complete Example

```
## tcp_handshake.scene - TCP Client-Server Communication
## Run with: kubrux tcp_handshake.scene

@actor server --host host353 --dir ~/lab --script server.txt
@actor client --host host353 --dir ~/lab --script client.txt
@layout vertical

## === ACT 1: SERVER SETUP ===
server: # Start a TCP server listening on port 9000
server: nc -l 9000

@pause 1.5

## === ACT 2: CLIENT CONNECTS ===
client: # Connect to the server
client: nc localhost 9000

@pause 1

## === ACT 3: DIALOGUE ===
client: @type Hello from the client!
client: @enter

@pause 1

server: @type Message received! Replying...
server: @enter

@pause 1

client: @type Goodbye!
client: @enter

@pause 1.5

## === CURTAIN ===
client: @ctrl-c
@pause 0.5
server: @ctrl-c
```

## Best Practices

1. **Use descriptive actor names**: `server`, `client`, `db` are better than `a`, `b`, `c`
2. **Add director's notes**: Use `##` comments to document acts and sections
3. **Use appropriate pauses**: Give processes time to start before interacting
4. **Record scripts**: Use `--script` to capture terminal output for later analysis
5. **Test locally first**: Use `--local` to test scenes before running on remote hosts
6. **Organize with sections**: Use comments to divide scenes into logical acts

## Common Patterns

### Starting a Service

```
server: # Start the service
server: ./start_service.sh
@pause 2  # Give it time to start
server: # Verify it's running
server: curl localhost:8080/health
```

### Interactive Commands

```
client: @type ssh user@host
client: @enter
@pause 1
client: @type password123
client: @enter
```

### Cleanup

```
## Cleanup
server: @ctrl-c
@pause 0.5
server: pkill -f service_name
server: rm -f /tmp/tempfile
```
