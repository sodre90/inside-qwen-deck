#!/bin/sh
# wrap the artifact body into a standalone page for the repo
SRC="$1"; DST="$2"
mkdir -p "$(dirname "$DST")"
{
  printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<style>:root{color-scheme:light}body{margin:0}img{max-width:100%%}[hidden]{display:none!important}</style>\n'
  sed -n '1,/^<\/style>$/p' "$SRC"
  printf '</head>\n<body>\n'
  sed '1,/^<\/style>$/d' "$SRC"
  printf '</body>\n</html>\n'
} > "$DST"
