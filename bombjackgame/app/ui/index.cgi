#!/bin/bash
# 炸弹杰克 CGI 入口：无端口、无后台进程
# 路由：
#   /                      -> www/index.html 及 www/ 下静态文件
#   /saves/<file>          -> 运行数据目录 var/saves/ 下的存档/按键/截图文件（只读）
#   /__list                -> 存档列表 JSON
#   /__save?name=<file>    -> POST 写入存档（POST body 为文件内容）
#   /__delete?name=<file>  -> 删除存档

# 从脚本自身位置定位目录（安装后脚本位于 <应用目录>/target/ui/index.cgi）
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$(cd "$SELF_DIR/.." && pwd)"
WWW_DIR="$TARGET_DIR/www"

# 运行数据目录：优先用系统标准挂载点，其次用 target 同级的 var
APP_ROOT="/var/apps/bombjackgame"
if [ -d "$APP_ROOT/var" ]; then
    VAR_DIR="$APP_ROOT/var"
else
    VAR_DIR="$(dirname "$TARGET_DIR")/var"
fi
SAVES_DIR="$VAR_DIR/saves"

URI_NO_QUERY="${REQUEST_URI%%\?*}"
QUERY_STRING="${QUERY_STRING:-}"
REL_PATH="/"
case "$URI_NO_QUERY" in
    *index.cgi*)
        REL_PATH="${URI_NO_QUERY#*index.cgi}"
        ;;
esac
REL_PATH="${REL_PATH:-/}"

send_status() {
    printf 'Status: %s\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n%s\n' "$1" "$2"
}

# 路径安全：拒绝目录穿越
case "$REL_PATH" in
    *..*)
        send_status "400 Bad Request" "Bad Request"
        exit 0
        ;;
esac

# ---------- 存档 API ----------
if [ "$REL_PATH" = "/__list" ] || [ "$REL_PATH" = "/__save" ] || [ "$REL_PATH" = "/__delete" ]; then
    mkdir -p "$SAVES_DIR/screenshots" 2>/dev/null
    if [ ! -d "$SAVES_DIR" ] || [ ! -w "$SAVES_DIR" ]; then
        send_status "500 Internal Server Error" "saves directory not writable: $SAVES_DIR"
        exit 0
    fi

    if [ "$REL_PATH" = "/__list" ]; then
        echo "Content-Type: application/json"
        echo ""
        printf '['
        first=1
        for f in "$SAVES_DIR"/*; do
            [ -f "$f" ] || continue
            name="$(basename "$f")"
            size="$(stat -c '%s' "$f" 2>/dev/null || stat -f '%z' "$f" 2>/dev/null || echo 0)"
            ts="$(stat -c '%Y' "$f" 2>/dev/null || echo 0)"
            mtime="$(date -d "@$ts" '+%Y-%m-%d %H:%M' 2>/dev/null || echo '-')"
            [ $first -eq 1 ] || printf ','
            printf '{"name":"%s","size":%s,"mtime":"%s","ts":%s}' "$name" "$size" "$mtime" "$ts"
            first=0
        done
        printf ']\n'
        exit 0
    fi

    # __save / __delete 需要合法的 name 参数（仅字母数字点下划线连字符）
    NAME="${QUERY_STRING#*name=}"
    NAME="${NAME%%&*}"
    case "$NAME" in
        ''|*[!A-Za-z0-9._-]*)
            send_status "400 Bad Request" "invalid name"
            exit 0
            ;;
    esac
    case "$NAME" in
        *.png) DEST="$SAVES_DIR/screenshots/$NAME" ;;
        *)     DEST="$SAVES_DIR/$NAME" ;;
    esac

    if [ "$REL_PATH" = "/__save" ]; then
        if [ "${REQUEST_METHOD:-GET}" != "POST" ]; then
            send_status "405 Method Not Allowed" "POST required"
            exit 0
        fi
        TMP="$DEST.tmp.$$"
        if [ -n "${CONTENT_LENGTH:-}" ] && [ "$CONTENT_LENGTH" -gt 0 ] 2>/dev/null; then
            head -c "$CONTENT_LENGTH" > "$TMP"
        else
            cat > "$TMP"
        fi
        if mv -f "$TMP" "$DEST" 2>/dev/null; then
            echo "Content-Type: application/json"
            echo ""
            printf '{"ok":true,"size":%s}\n' "$(stat -c '%s' "$DEST" 2>/dev/null || echo 0)"
        else
            rm -f "$TMP"
            send_status "500 Internal Server Error" "write failed"
        fi
        exit 0
    fi

    # __delete
    rm -f "$DEST" 2>/dev/null
    echo "Content-Type: application/json"
    echo ""
    printf '{"ok":true}\n'
    exit 0
fi

# ---------- saves 目录只读访问（读档 / 按键配置） ----------
case "$REL_PATH" in
    /saves/*)
        FILE_NAME="${REL_PATH#/saves/}"
        case "$FILE_NAME" in
            *.png) SRC_FILE="$SAVES_DIR/screenshots/$FILE_NAME" ;;
            *)     SRC_FILE="$SAVES_DIR/$FILE_NAME" ;;
        esac
        if [ -f "$SRC_FILE" ]; then
            case "${SRC_FILE##*.}" in
                json) mime="application/json; charset=utf-8" ;;
                png)  mime="image/png" ;;
                *)    mime="application/octet-stream" ;;
            esac
            echo "Content-Type: $mime"
            echo ""
            cat "$SRC_FILE"
        else
            send_status "404 Not Found" "Not Found"
        fi
        exit 0
        ;;
esac

# ---------- 静态文件 ----------
if [ -z "$REL_PATH" ] || [ "$REL_PATH" = "/" ]; then
    REL_PATH="/index.html"
fi
TARGET_FILE="$WWW_DIR$REL_PATH"

if [ ! -f "$TARGET_FILE" ]; then
    send_status "404 Not Found" "404 Not Found"
    exit 0
fi

case "${TARGET_FILE##*.}" in
    html|htm)  mime="text/html; charset=utf-8" ;;
    css)       mime="text/css; charset=utf-8" ;;
    js)        mime="application/javascript; charset=utf-8" ;;
    json)      mime="application/json; charset=utf-8" ;;
    png)       mime="image/png" ;;
    jpg|jpeg)  mime="image/jpeg" ;;
    ico)       mime="image/x-icon" ;;
    svg)       mime="image/svg+xml" ;;
    wasm)      mime="application/wasm" ;;
    nes)       mime="application/octet-stream" ;;
    *)         mime="application/octet-stream" ;;
esac

LEN="$(stat -c '%s' "$TARGET_FILE" 2>/dev/null || echo '')"
echo "Content-Type: $mime"
if [ -n "$LEN" ]; then
    echo "Content-Length: $LEN"
fi
echo ""
cat "$TARGET_FILE"
exit 0
