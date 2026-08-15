#!/usr/bin/env bash
# Capture one application window as a PNG for a deck slide.
#
#   bash capture-window.sh <out.png> ["<App Name>"] [inset]
#
# Examples
#   bash capture-window.sh assets/product/desktop/claude-desktop.png "Claude"
#   bash capture-window.sh assets/product/terminal/claude-code.png
#
# Two modes, chosen automatically:
#
#   AUTOMATIC, used when an app name is given AND the terminal running this
#   has Accessibility permission. Brings the app forward, reads its front
#   window's bounds, captures exactly that rectangle, hands focus back. Nothing
#   else on screen is captured.
#
#   INTERACTIVE, the fallback, and the mode used when no app name is given.
#   You click the window you want. Needs only Screen Recording permission.
#
# Permissions, both in System Settings → Privacy & Security:
#   Screen Recording  : required for either mode
#   Accessibility     : optional, unlocks the automatic mode
# Grant them to the terminal application you run this from, then restart it.
# A blank or wallpaper-only PNG means Screen Recording was denied.
set -uo pipefail

OUT="${1:?output png path required, e.g. assets/product/desktop/claude-desktop.png}"
APP="${2:-}"
INSET="${3:-0}"

mkdir -p "$(dirname "$OUT")"

interactive() {
  echo "Interactive capture. Click the window you want to photograph."
  echo "Press Escape to cancel."
  screencapture -w -o -t png "$OUT"
}

if [ -z "$APP" ]; then
  interactive
else
  PREV=$(osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>/dev/null || true)
  osascript -e "tell application \"$APP\" to activate" >/dev/null 2>&1 || {
    echo "Could not activate \"$APP\". Is it installed and named exactly that?" >&2
    exit 1
  }
  sleep 1.2

  BOUNDS=$(osascript 2>/dev/null <<EOF
tell application "System Events" to tell process "$APP"
  set {x, y} to position of front window
  set {w, h} to size of front window
  return (x as string) & "," & (y as string) & "," & (w as string) & "," & (h as string)
end tell
EOF
)

  if [ -n "$BOUNDS" ]; then
    IFS=',' read -r X Y W H <<< "$BOUNDS"
    X=$((X + INSET)); Y=$((Y + INSET))
    W=$((W - INSET * 2)); H=$((H - INSET * 2))
    screencapture -x -R"${X},${Y},${W},${H}" -t png "$OUT"
    [ -n "$PREV" ] && osascript -e "tell application \"System Events\" to set frontmost of process \"$PREV\" to true" >/dev/null 2>&1
  else
    echo "No Accessibility permission, so window bounds are unavailable."
    echo "Falling back to interactive capture. $APP is now frontmost."
    interactive
  fi
fi

if [ ! -f "$OUT" ]; then
  echo "Nothing was captured." >&2
  exit 1
fi

echo "$OUT ($(sips -g pixelWidth -g pixelHeight "$OUT" | awk '/pixel/{printf "%s ", $2}')px)"
