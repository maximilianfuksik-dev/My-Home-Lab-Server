#!/bin/bash
# ===================================================
# HOME LAB SERVER - SMART BACKUP BASH
# ==================================================


BACKUP_DIR="/home/backupuser"
TARGET_DIR="/home/max/archives"
STATUS_FILE="/home/max/.backup_last_chars.txt"
TIMESTAMP=$(date + "%y-%m-%d_%H-%M-%S")
ARCHIVE_NAME="learning_notes_$TIMESTAMP.tar.gz"

#WEBHOOK
DISCORD_URL="DISCORD_BOT_URL" 

echo "[i] Starting smart server backup at $(date)"

# CREATE TARGET DIRECTORY IF NOT EXIST
mkdir -p "$TARGET_DIR"

# CALCULATE METRICS AND STATISTICS
echo "[*] Analyzing learning materials..."

FILE_COUNT=$(sudo find "$BACKUP_DIR" -type f ! -path "*/.*" | wc -l)
DIR_COUNT=$(sudo find "$BACKUP_DIR" -type d ! -path "*/.*" ! -path "$BACKUP_DIR" | wc -l)
CURRENT_CHARS=$(sudo find "$BACKUP_DIR" -type f ! -path "*/.*" -exec cat {} + | wc -m)

# Check if a previous state exists for delta calulation

if [ -f "$STATUS_FILE" ]; then
        LAST_CHARS=$(cat "STATUS_FILE")
else
        LAST_CHARS=0
fi

DIFF_CHARS=$((CURRENT_CHARS - LAST_CHARS))


# Format the prefix for the delta display
if [ "$DIFF_CHARS" -gt 0 ]; then
        DIFF_DISPLAY="+$DIFF_CHARS"
else
        DIFF_DISPLAY="$DIFF_CHARS"

fi

echo "----------------------------------------------------"
echo "LEARNING STATISTICS"
echo " -> Total Directories: $DIR_COUNT"
echo " -> Total Files: $FILE_COUNT"
echo " -> Total Characters: $CURRENT_CHARS"
echo " -> New since last Time: $DIFF_DISPLAY  character"
echo "----------------------------------------------------"
# SAVE CURRENT CHARACTER COUNT FOR NETXT PROGRESSION CHECK
echo "$CURRENT_CHARS" > "$STATUS_FILE"

# COMPRESS INGESTED DATA INTO TARBALL
echo "[*] Creating compressed archive..."
sudo tar -czf "$TARGET_DIR/$ARCHIVE_NAME" --exclude='.*/' -C "$BACKUP_DIR" .

# HEALTH CHECK & DISCORD NOTFICATION PIPELINE
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Backup archived as: $ARCHIVE_NAME"
    echo "====================================================================="

    # Safe decoupled JSON payload generation without emojis
    echo "{" > /tmp/discord.json
    echo "  \"content\": \"SUCCESS - Home-Lab Backup Completed!\nArchive: $ARCHIVE_NAME\n\nStatistics:\nDirectories: $DIR_COUNT\nFiles: $FILE_COUNT\nTotal Characters: $CURRENT_CHARS\nNew Progress: $DIFF_DISPL>
    echo "}" >> /tmp/discord.json

    curl -H "Content-Type: application/json" -X POST -d @/tmp/discord.json "$DISCORD_URL"
    rm -f /tmp/discord.json
else
    echo "[ERROR] Backup compaction failed!"
    echo "====================================================================="

    curl -H "Content-Type: application/json" -X POST -d "{\"content\": \"ERROR - Automated backup execution failed on the Home-Lab-Server!\"}" "$DISCORD_URL"
fi
