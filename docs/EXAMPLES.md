# Examples

This document provides example scene files and use cases for kubrux.

## Table of Contents

1. [Simple Single-Actor Scene](#simple-single-actor-scene)
2. [TCP Client-Server](#tcp-client-server)
3. [Message Relay](#message-relay)
4. [Distributed System](#distributed-system)
5. [Interactive SSH Session](#interactive-ssh-session)
6. [Network Testing](#network-testing)
7. [Database Operations](#database-operations)

## Simple Single-Actor Scene

**File:** `simple.scene`

A basic scene demonstrating single-actor mode with system information gathering.

```bash
## simple.scene - A single-actor scene
## Run with: kubrux simple.scene

@actor client --host host353 --dir ~/csci353/lab1 --script demo.txt

client: # Show where we are
client: pwd

client: # List files in the lab directory
client: ls -la

@pause 1

client: # Check our IP address
client: hostname -I

@pause 1

client: # Show network interfaces
client: ip link show

@pause 2

client: echo "Scene complete."
```

**Run:**
```bash
kubrux simple.scene
```

## TCP Client-Server

**File:** `tcp_handshake.scene`

Demonstrates basic TCP communication using netcat.

```bash
## tcp_handshake.scene - TCP Client-Server Communication
## Run with: kubrux tcp_handshake.scene

@actor server --host host353 --dir ~/csci353/lab2 --script server.txt
@actor client --host host353 --dir ~/csci353/lab2 --script client.txt
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

**Run:**
```bash
kubrux tcp_handshake.scene
```

## Message Relay

**File:** `relay.scene`

Shows message passing through an intermediary relay node.

```bash
## relay.scene - Three-Way Message Relay
## Run with: kubrux relay.scene

@actor alice --host host353 --dir ~ --script alice.txt
@actor relay --host host353 --dir ~ --script relay.txt
@actor bob   --host host353 --dir ~ --script bob.txt
@layout vertical

## === ACT 1: SETUP THE RELAY ===
relay: # Relay node: listen on 8001, forward to 8002
relay: # Using named pipes for bidirectional relay
relay: mkfifo /tmp/fifo1 /tmp/fifo2 2>/dev/null || true

@pause 0.5

relay: # Start the relay (simplified - just show concept)
relay: nc -l 8001 | tee /tmp/relay.log | nc -l 8002 &

@pause 1

## === ACT 2: BOB CONNECTS ===
bob: # Bob connects to receive from relay
bob: nc localhost 8002

@pause 1

## === ACT 3: ALICE SENDS ===
alice: # Alice connects to send through relay
alice: nc localhost 8001

@pause 1

alice: @type Hello Bob, this goes through the relay!
alice: @enter

@pause 2

## === ACT 4: EXAMINE THE RELAY ===
relay: # Check what the relay captured
relay: cat /tmp/relay.log

@pause 2

## === CURTAIN ===
alice: @ctrl-c
bob: @ctrl-c
relay: @ctrl-c

@pause 0.5

relay: rm -f /tmp/fifo1 /tmp/fifo2 /tmp/relay.log
relay: pkill -f "nc -l 800" || true
relay: echo "Relay scene complete"
```

## Distributed System

**File:** `distributed.scene`

Demonstrates a multi-host distributed system with database, application server, and client.

```bash
## distributed.scene - Multi-Host Distributed System
## Run with: kubrux distributed.scene

@actor db      --host db.example.com     --dir ~/app/db      --script db.txt
@actor app     --host app.example.com    --dir ~/app/server  --script app.txt
@actor client  --host client.example.com --dir ~/app/client  --script client.txt
@layout vertical

## === ACT 1: DATABASE ===
db: # Starting PostgreSQL database
db: pg_ctl start -D ./data -l logfile

@pause 3

db: # Verify database is running
db: pg_isready

@pause 1

## === ACT 2: APPLICATION SERVER ===
app: # Starting application server
app: ./start_server.sh --db-host db.example.com

@pause 2

app: # Check server status
app: curl -s localhost:8080/health

@pause 1

## === ACT 3: CLIENT REQUESTS ===
client: # Making API request
client: curl -X GET http://app.example.com:8080/api/users

@pause 2

client: # Creating a new user
client: curl -X POST http://app.example.com:8080/api/users -d '{"name": "test"}'

@pause 2

## === ACT 4: VERIFY ===
db: # Check database for new record
db: psql -c "SELECT * FROM users ORDER BY id DESC LIMIT 5;"

@pause 2

## === CURTAIN ===
client: echo "Client complete"
app: @ctrl-c
@pause 0.5
db: pg_ctl stop -D ./data
```

## Interactive SSH Session

**File:** `ssh_session.scene`

Demonstrates an interactive SSH login with password entry.

```bash
## ssh_session.scene - Interactive SSH Login
## Run with: kubrux ssh_session.scene --local

@actor local --local --dir ~

local: # Connect to remote server
local: @type ssh user@remote.example.com
local: @enter

@pause 2

local: # Enter password (simulated)
local: @type mypassword123
local: @enter

@pause 1

local: # Now we're logged in
local: pwd

@pause 1

local: # Run a command
local: ls -la

@pause 1

local: # Exit
local: @type exit
local: @enter
```

## Network Testing

**File:** `network_test.scene`

Demonstrates network connectivity testing between multiple hosts.

```bash
## network_test.scene - Network Connectivity Testing
## Run with: kubrux network_test.scene

@actor host1 --host host1.example.com --dir ~ --script host1.txt
@actor host2 --host host2.example.com --dir ~ --script host2.txt
@layout horizontal

## === ACT 1: GATHER IP ADDRESSES ===
host1: # Get host1 IP address
host1: hostname -I | awk '{print $1}'

@pause 1

host2: # Get host2 IP address
host2: hostname -I | awk '{print $1}'

@pause 1

## === ACT 2: PING TEST ===
host1: # Ping host2
host1: ping -c 3 host2.example.com

@pause 2

host2: # Ping host1
host2: ping -c 3 host1.example.com

@pause 2

## === ACT 3: PORT SCAN ===
host1: # Check if port 22 is open on host2
host1: nc -zv host2.example.com 22

@pause 1

host2: # Check if port 22 is open on host1
host2: nc -zv host1.example.com 22

@pause 1

## === CURTAIN ===
host1: echo "Host1 test complete"
host2: echo "Host2 test complete"
```

## Database Operations

**File:** `database_ops.scene`

Demonstrates database operations with a client-server setup.

```bash
## database_ops.scene - Database Operations Demo
## Run with: kubrux database_ops.scene

@actor db --host db.example.com --dir ~/db --script db.txt
@actor client --host client.example.com --dir ~/app --script client.txt
@layout vertical

## === ACT 1: START DATABASE ===
db: # Start database server
db: ./start_db.sh

@pause 3

db: # Verify database is ready
db: ./check_db.sh

@pause 1

## === ACT 2: CLIENT CONNECTS ===
client: # Connect to database
client: psql -h db.example.com -U appuser -d myapp

@pause 2

## === ACT 3: DATABASE OPERATIONS ===
client: # Create a table
client: @type CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100));
client: @enter

@pause 1

client: # Insert data
client: @type INSERT INTO users (name) VALUES ('Alice'), ('Bob');
client: @enter

@pause 1

client: # Query data
client: @type SELECT * FROM users;
client: @enter

@pause 1

## === ACT 4: CLEANUP ===
client: # Exit psql
client: @type \q
client: @enter

@pause 0.5

db: # Stop database
db: ./stop_db.sh
```

## Tips for Writing Scenes

1. **Start Simple**: Begin with single-actor scenes to understand the format
2. **Use Pauses**: Give processes time to start before interacting
3. **Record Scripts**: Use `--script` to capture output for debugging
4. **Test Locally**: Use `--local` to test scenes before running on remote hosts
5. **Document Acts**: Use `##` comments to organize your scenes
6. **Clean Up**: Always include cleanup steps (Ctrl+C, exit, etc.)
7. **Error Handling**: Consider what happens if a command fails

## Running Examples

All example scenes can be run with:

```bash
# Basic usage
kubrux example.scene

# With recording
kubrux example.scene --script output.log

# Local execution
kubrux example.scene --local

# Custom session name
kubrux example.scene --session my_session
```

Watch the performance in another terminal:

```bash
tmux attach -t kubrux
```
