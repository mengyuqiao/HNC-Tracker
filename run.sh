#!/bin/bash
# Run HNC Tracker + ngrok tunnel
# Usage: bash run.sh

cd "$(dirname "$0")"

# ── Resolve conda base ───────────────────────────────────────────────────────
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda3")
ACTIVATE="source $CONDA_BASE/etc/profile.d/conda.sh && conda activate hnc-tracker"

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$(pwd)/$LOG_DIR/hnc-tracker-$(date +%Y%m%d-%H%M%S).log"

echo "============================================"
echo "  HNC Tracker starting..."
echo "  Public URL will appear in top-right pane"
echo "  Logs: $LOG_FILE"
echo "============================================"

# ── Helper: send bash + conda activate to a pane, then a command ─────────────
activate_pane() {
  local pane=$1
  local cmd=$2
  tmux send-keys -t $pane "bash" Enter
  tmux send-keys -t $pane "$ACTIVATE" Enter
  tmux send-keys -t $pane "$cmd" Enter
}

# ── Launch tmux ──────────────────────────────────────────────────────────────
SESSION="hnc"
tmux kill-session -t $SESSION 2>/dev/null
tmux new-session -d -s $SESSION -x 220 -y 50

# Pane 0 (left): Flask
activate_pane $SESSION:0.0 "python -u app.py 2>&1 | tee $LOG_FILE"

# Pane 1 (top right): ngrok
tmux split-window -h -t $SESSION:0.0
activate_pane $SESSION:0.1 "sleep 6 && ngrok http 5000"

# Pane 2 (bottom right): live log tail
tmux split-window -v -t $SESSION:0.1
activate_pane $SESSION:0.2 "sleep 3 && tail -f $LOG_FILE"

# Focus Flask pane
tmux select-pane -t $SESSION:0.0

tmux attach -t $SESSION