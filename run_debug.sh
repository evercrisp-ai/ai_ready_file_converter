#!/bin/bash
# Debug script to capture all output from the app
LOG_FILE="/Users/benscooper/ai-ready-file-converter/.cursor/terminal_output.log"
echo "=== Starting app at $(date) ===" > "$LOG_FILE"
"/Users/benscooper/ai-ready-file-converter/dist/AI Ready File Converter.app/Contents/MacOS/AI Ready File Converter" 2>&1 | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "=== App exited at $(date) ===" >> "$LOG_FILE"
