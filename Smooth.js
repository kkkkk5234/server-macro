TAG="shizuku_gaming_fps"
STORE="/data/local/tmp/${TAG}_backup"
BK="${STORE}/kv_backup.txt"

[ -f "$BK" ] || { echo "[${TAG}] No backup."; exit 0; }

while IFS='=' read -r k v; do
  [ -z "$k" ] && continue
  ns="${k%%.*}"; key="${k#*.}"
  settings put "$ns" "$key" "$v" >/dev/null 2>&1 || true
done < "$BK"

echo "[${TAG}] reset done"
