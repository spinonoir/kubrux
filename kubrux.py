#!/usr/bin/env python3
"""
kubrux - deterministic multi-terminal scene direction using tmux
"""

import libtmux
import time
import argparse
import shlex
import re
import inspect
import logging
import sys
import subprocess
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

__version__ = "1.1.0"

# Configure logging
logger = logging.getLogger("kubrux")

# libtmux's Pane.send_keys kwarg changed across versions (literal vs literally)
_SEND_KEYS_LITERAL_KWARG: Optional[str] = None
_SEND_KEYS_LITERAL_KWARG_DETERMINED = False


def _determine_send_keys_literal_kwarg(pane: libtmux.Pane) -> None:
    global _SEND_KEYS_LITERAL_KWARG_DETERMINED, _SEND_KEYS_LITERAL_KWARG
    if _SEND_KEYS_LITERAL_KWARG_DETERMINED:
        return

    _SEND_KEYS_LITERAL_KWARG_DETERMINED = True
    kw = None
    try:
        # inspect.signature might fail on some python/libtmux versions
        params = inspect.signature(pane.send_keys).parameters
        if "literal" in params:
            kw = "literal"
        elif "literally" in params:
            kw = "literally"
    except Exception as e:
        logger.debug(f"inspect.signature failed: {e}; will rely on fallback detection")

    _SEND_KEYS_LITERAL_KWARG = kw
    logger.debug(f"Determined send_keys literal kwarg: {kw}")


def _send_keys_literal_compat(pane: libtmux.Pane, keys: str, enter: bool, literal_flag: bool) -> None:
    global _SEND_KEYS_LITERAL_KWARG
    _determine_send_keys_literal_kwarg(pane)

    kw = _SEND_KEYS_LITERAL_KWARG
    
    # 1. Try the detected kwarg
    if kw == "literal":
        try:
            pane.send_keys(keys, enter=enter, literal=literal_flag)
            return
        except TypeError:
            logger.warning("TypeError using 'literal', attempting fallback...")
            _SEND_KEYS_LITERAL_KWARG = "literally"
    elif kw == "literally":
        try:
            pane.send_keys(keys, enter=enter, literally=literal_flag)
            return
        except TypeError:
            logger.warning("TypeError using 'literally', attempting fallback...")
            _SEND_KEYS_LITERAL_KWARG = "literal"

    # 2. If unknown or failed, try brute force
    try:
        pane.send_keys(keys, enter=enter, literal=literal_flag)
        _SEND_KEYS_LITERAL_KWARG = "literal"
        return
    except TypeError:
        pass
        
    try:
        pane.send_keys(keys, enter=enter, literally=literal_flag)
        _SEND_KEYS_LITERAL_KWARG = "literally"
        return
    except TypeError:
        pass

    logger.warning("send_keys does not accept literal/literally; sending without raw flag.")
    pane.send_keys(keys, enter=enter)


@dataclass
class ActorConfig:
    """Configuration for a single actor."""
    name: str
    host: Optional[str] = None
    working_dir: Optional[str] = None
    script_file: Optional[str] = None
    is_local: bool = False
    pane: Optional[libtmux.Pane] = None


class Kubrux:
    """
    The director. Interprets scene files and commands actors with precision.
    """
    
    def __init__(self, session_name: str = "kubrux"):
        logger.info(f"Initializing Session: {session_name}")
        self.server = libtmux.Server()
        
        # Kill existing session if present
        existing = self.server.sessions.filter(session_name=session_name)
        if existing:
            logger.info(f"Killing existing session: {session_name}")
            existing[0].kill()
        
        self.session = self.server.new_session(session_name=session_name)
        
        # Cast management
        self.cast: dict[str, ActorConfig] = {}
        self.lead_actor: Optional[str] = None
        self.layout = "vertical"
        
        # Timing controls
        self.typing_delay = 0.04
        self.line_pause = 1.0
    
    def add_actor(self, config: ActorConfig):
        """Add an actor to the cast and prepare their stage (pane)."""
        logger.info(f"Adding actor: {config.name} (Host: {config.host}, Local: {config.is_local})")

        if not self.cast:
            config.pane = self.session.active_window.active_pane
        else:
            first_pane = list(self.cast.values())[0].pane
            vertical = self.layout == "vertical"
            config.pane = first_pane.split_window(vertical=vertical)
        
        self.cast[config.name] = config
        
        if self.lead_actor is None:
            self.lead_actor = config.name
        
        time.sleep(0.5)
        self._prepare_actor(config)
        
        # Balance the stage
        layout_name = "even-vertical" if self.layout == "vertical" else "even-horizontal"
        self.session.active_window.select_layout(layout_name)
    
    def _prepare_actor(self, config: ActorConfig):
        """Get actor into position (SSH, cd, start script)."""
        logger.debug(f"Preparing actor {config.name}...")
        
        if not config.is_local and config.host:
            cmd = f"ssh {config.host}"
            logger.info(f"[{config.name}] Connecting: {cmd}")
            config.pane.send_keys(cmd, enter=True)
            # This is a common failure point if SSH takes > 2s
            time.sleep(2)
        
        if config.working_dir:
            cmd = f"cd {config.working_dir}"
            logger.debug(f"[{config.name}] Changing dir: {cmd}")
            config.pane.send_keys(cmd, enter=True)
            time.sleep(0.5)
        
        if config.script_file:
            cmd = f"script {config.script_file}"
            logger.debug(f"[{config.name}] Recording: {cmd}")
            config.pane.send_keys(cmd, enter=True)
            time.sleep(0.5)
    
    def _get_pane(self, actor: str = None) -> libtmux.Pane:
        """Get an actor's stage (pane)."""
        if actor is None:
            actor = self.lead_actor
        
        if actor not in self.cast:
            raise ValueError(f"Unknown actor: {actor}")
        
        return self.cast[actor].pane
    
    def deliver_line(self, line: str, actor: str = None):
        """Actor types and delivers a line (command)."""
        target = actor or self.lead_actor
        logger.info(f"Action [{target}]: {line}")
        pane = self._get_pane(actor)
        
        for char in line:
            _send_keys_literal_compat(pane, keys=char, enter=False, literal_flag=True)
            time.sleep(self.typing_delay)
        
        time.sleep(0.2)
        pane.send_keys("", enter=True)
        time.sleep(self.line_pause)
    
    def type_without_enter(self, text: str, actor: str = None):
        """Actor types but holds (no Enter)."""
        target = actor or self.lead_actor
        logger.debug(f"Typing [{target}]: {text}")
        pane = self._get_pane(actor)
        
        for char in text:
            _send_keys_literal_compat(pane, keys=char, enter=False, literal_flag=True)
            time.sleep(self.typing_delay)
        
        time.sleep(0.2)
    
    def send_instant(self, command: str, actor: str = None):
        """Instant delivery, no typing effect."""
        logger.debug(f"Instant Send [{actor or self.lead_actor}]: {command}")
        pane = self._get_pane(actor)
        pane.send_keys(command, enter=True)
        time.sleep(self.line_pause)
    
    def send_enter(self, actor: str = None):
        logger.debug(f"Enter [{actor or self.lead_actor}]")
        pane = self._get_pane(actor)
        pane.send_keys("", enter=True)
        time.sleep(0.3)
    
    def ctrl_c(self, actor: str = None):
        logger.debug(f"Ctrl+C [{actor or self.lead_actor}]")
        self._get_pane(actor).send_keys("C-c")
        time.sleep(0.3)
    
    def ctrl_d(self, actor: str = None):
        logger.debug(f"Ctrl+D [{actor or self.lead_actor}]")
        self._get_pane(actor).send_keys("C-d")
        time.sleep(0.3)
    
    def ctrl_z(self, actor: str = None):
        logger.debug(f"Ctrl+Z [{actor or self.lead_actor}]")
        self._get_pane(actor).send_keys("C-z")
        time.sleep(0.3)
    
    def send_key(self, key: str, actor: str = None):
        logger.debug(f"Key {key} [{actor or self.lead_actor}]")
        self._get_pane(actor).send_keys(key)
        time.sleep(0.3)
    
    def clear_stage(self, actor: str = None):
        self._get_pane(actor).send_keys("clear", enter=True)
        time.sleep(0.3)
    
    def wrap(self):
        """That's a wrap - stop all script recordings."""
        logger.info("Wrapping up scene...")
        for config in self.cast.values():
            if config.script_file:
                config.pane.send_keys("exit", enter=True)
                time.sleep(0.3)
    
    def _parse_actor_directive(self, line: str) -> ActorConfig:
        parts = shlex.split(line)
        parts.pop(0)  # Remove @actor
        
        if not parts:
            raise ValueError("@actor requires a name")
        
        name = parts.pop(0)
        config = ActorConfig(name=name)
        
        while parts:
            opt = parts.pop(0)
            if opt == "--host" and parts:
                config.host = parts.pop(0)
            elif opt == "--dir" and parts:
                config.working_dir = parts.pop(0)
            elif opt == "--script" and parts:
                config.script_file = parts.pop(0)
            elif opt == "--local":
                config.is_local = True
        
        return config
    
    def _process_direction(self, direction: str, actor: str = None):
        """Process a stage direction (@directive)."""
        logger.debug(f"Directive: {direction}")
        
        if direction.startswith("@pause "):
            seconds = float(direction.split(maxsplit=1)[1])
            logger.debug(f"Pausing {seconds}s")
            time.sleep(seconds)
        
        elif direction.startswith("@delay "):
            val = float(direction.split(maxsplit=1)[1])
            self.typing_delay = val
            logger.debug(f"Typing delay set to {val}")
        
        elif direction.startswith("@wait "):
            val = float(direction.split(maxsplit=1)[1])
            self.line_pause = val
            logger.debug(f"Line wait set to {val}")
        
        elif direction == "@ctrl-c":
            self.ctrl_c(actor)
        elif direction == "@ctrl-d":
            self.ctrl_d(actor)
        elif direction == "@ctrl-z":
            self.ctrl_z(actor)
        elif direction.startswith("@key "):
            key = direction.split(maxsplit=1)[1]
            self.send_key(key, actor)
        elif direction == "@clear":
            self.clear_stage(actor)
        elif direction.startswith("@send "):
            command = direction.split(maxsplit=1)[1]
            self.send_instant(command, actor)
        elif direction.startswith("@type "):
            text = direction.split(maxsplit=1)[1]
            self.type_without_enter(text, actor)
        elif direction == "@enter":
            self.send_enter(actor)
    
    def direct(self, scene_file: Path, default_host: str = None,
               default_dir: str = None, default_script: str = None,
               default_local: bool = False):
        
        logger.info(f"Directing scene file: {scene_file}")
        content = scene_file.read_text()
        lines = content.splitlines()
        
        # First pass: casting call
        for line in lines:
            line = line.rstrip()
            if line.startswith("@actor "):
                config = self._parse_actor_directive(line)
                self.add_actor(config)
            elif line.startswith("@layout "):
                self.layout = line.split(maxsplit=1)[1].strip()
        
        # If no actors defined, single-actor scene
        if not self.cast:
            logger.info("No @actor directives found; creating default actor from CLI args")
            config = ActorConfig(
                name="default",
                host=default_host,
                working_dir=default_dir,
                script_file=default_script,
                is_local=default_local
            )
            self.add_actor(config)
        
        # Second pass: action!
        for line in lines:
            line = line.rstrip()
            
            if not line or line.startswith("##") or line.startswith("@actor ") or line.startswith("@layout "):
                continue
            
            # Check for actor prefix (actor: dialogue)
            actor = None
            match = re.match(r'^(\w+):\s*(.*)$', line)
            if match and match.group(1) in self.cast:
                actor = match.group(1)
                line = match.group(2)
            
            if not line:
                continue
            
            if line.startswith("@"):
                self._process_direction(line, actor)
            else:
                self.deliver_line(line, actor)


def get_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser. Used for CLI and shtab completion generation."""
    parser = argparse.ArgumentParser(
        prog="kubrux",
        description="Deterministic multi-terminal scene direction using tmux",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("scene_file", type=Path, nargs="?", help="Scene file (*.scene)")
    parser.add_argument("--host", help="Default SSH host")
    parser.add_argument("--dir", "-d", dest="working_dir", help="Default working directory")
    parser.add_argument("--script", "-s", dest="script_file", help="Default script recording filename")
    parser.add_argument("--session", default="kubrux", help="tmux session name (default: kubrux)")
    parser.add_argument("--local", action="store_true", help="Run locally, no SSH")
    parser.add_argument("--help-scene", action="store_true", help="Show detailed scene file format")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--attach",
        "-a",
        action="store_true",
        help="Attach this terminal to the tmux session to watch the scene live",
    )
    try:
        import shtab
        shtab.add_argument_to(parser, "--print-completion")
    except ImportError:
        pass
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    # Handle --print-completion (from shtab) before any other logic
    if hasattr(args, "print_completion") and args.print_completion:
        import shtab
        print(shtab.complete(parser, shell=args.print_completion))
        return 0
    
    if args.help_scene:
        print(__doc__)
        return 0

    if not args.scene_file:
        parser.error("the following arguments are required: scene_file")
    
    # Setup logging based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr
    )

    if not args.scene_file.exists():
        print(f"Scene not found: {args.scene_file}")
        return 1
    
    director = Kubrux(session_name=args.session)
    
    print(f"🎬 Directing: {args.scene_file}")
    print(f"📺 Watch: tmux attach -t {args.session}")

    exit_code = 0

    def run_scene():
        nonlocal exit_code
        try:
            director.direct(
                args.scene_file,
                default_host=args.host,
                default_dir=args.working_dir,
                default_script=args.script_file,
                default_local=args.local,
            )
            director.wrap()
            print("🎬 That's a wrap!")
            exit_code = 0
        except KeyboardInterrupt:
            print("\n🛑 Director interrupted!")
            exit_code = 1
        except Exception:
            logger.exception("Fatal error during scene execution")
            exit_code = 1

    if args.attach:
        # Run the scene in a background thread so we can attach this terminal
        # to the tmux session and watch the action live.
        scene_thread = threading.Thread(target=run_scene, daemon=False)
        scene_thread.start()

        try:
            subprocess.run(["tmux", "attach", "-t", args.session], check=False)
        except FileNotFoundError:
            print(
                "tmux binary not found; cannot auto-attach. "
                f"You can manually run 'tmux attach -t {args.session}' if tmux is installed."
            )

        scene_thread.join()
        return exit_code
    else:
        run_scene()
        return exit_code


if __name__ == "__main__":
    exit(main())