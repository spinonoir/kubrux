#!/usr/bin/env bash
#
# Bash completion for kubrux
#
# Usage (bash):
#   source /path/to/kubrux/completions/kubrux.bash
#
# Or install system-wide (bash-completion):
#   sudo install -m 0644 completions/kubrux.bash /usr/local/etc/bash_completion.d/kubrux
#

_kubrux__uniq_lines() {
  # Read lines on stdin, output unique lines (stable, no sort dependency).
  awk 'NF && !seen[$0]++ { print }'
}

_kubrux__ssh_hosts() {
  # Suggest hostnames from ssh config, known_hosts, and system hostnames.
  local cfg

  {
    for cfg in "$HOME/.ssh/config" "/etc/ssh/ssh_config"; do
      [[ -r "$cfg" ]] || continue
      # Host entries can be: Host foo bar baz
      # Ignore wildcard patterns (contain * ? !).
      awk '
        tolower($1)=="host" {
          for (i=2; i<=NF; i++) {
            h=$i
            if (h ~ /[*?!]/) continue
            print h
          }
        }
      ' "$cfg"
    done

    # Known hosts (ignore hashed entries, strip brackets and ports).
    if [[ -r "$HOME/.ssh/known_hosts" ]]; then
      awk '
        $1 ~ /^\|/ { next }            # hashed
        {
          split($1, a, ",")
          for (i in a) {
            h=a[i]
            gsub(/^\[/, "", h); gsub(/\](:[0-9]+)?$/, "", h)
            if (h != "") print h
          }
        }
      ' "$HOME/.ssh/known_hosts"
    fi

    # System hostnames known to bash.
    compgen -A hostname 2>/dev/null || true
  } 2>/dev/null | _kubrux__uniq_lines
}

_kubrux__tmux_sessions() {
  command -v tmux >/dev/null 2>&1 || return 0
  tmux list-sessions -F '#S' 2>/dev/null | _kubrux__uniq_lines
}

_kubrux() {
  local cur prev words cword

  # Prefer bash-completion's helper if present.
  if declare -F _init_completion >/dev/null 2>&1; then
    _init_completion -n : || return
  else
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    words=("${COMP_WORDS[@]}")
    cword="$COMP_CWORD"
  fi

  local opts
  opts="--host --dir -d --script -s --session --local --attach -a --verbose -v --help-scene --version -h --help"

  case "$prev" in
    --host)
      mapfile -t COMPREPLY < <(compgen -W "$(_kubrux__ssh_hosts)" -- "$cur")
      return 0
      ;;
    --session)
      mapfile -t COMPREPLY < <(compgen -W "$(_kubrux__tmux_sessions)" -- "$cur")
      return 0
      ;;
    --dir|-d)
      if declare -F compopt >/dev/null 2>&1; then
        compopt -o dirnames 2>/dev/null || true
      fi
      mapfile -t COMPREPLY < <(compgen -d -- "$cur")
      return 0
      ;;
    --script|-s)
      if declare -F compopt >/dev/null 2>&1; then
        compopt -o filenames 2>/dev/null || true
      fi
      mapfile -t COMPREPLY < <(compgen -f -- "$cur")
      return 0
      ;;
  esac

  # If completing an option, propose flags.
  if [[ "$cur" == -* ]]; then
    mapfile -t COMPREPLY < <(compgen -W "$opts" -- "$cur")
    return 0
  fi

  # Otherwise complete the positional scene file.
  if declare -F compopt >/dev/null 2>&1; then
    compopt -o filenames 2>/dev/null || true
  fi

  # Prefer *.scene, fall back to any file.
  local scene_suggestions
  scene_suggestions="$(compgen -f -- "$cur" | awk -F/ '$NF ~ /\.scene$/ { print }')"
  if [[ -n "$scene_suggestions" ]]; then
    mapfile -t COMPREPLY < <(printf '%s\n' "$scene_suggestions")
  else
    mapfile -t COMPREPLY < <(compgen -f -- "$cur")
  fi
}

complete -F _kubrux kubrux

