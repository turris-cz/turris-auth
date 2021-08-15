#!/bin/sh
set -eu
dest="${1:-}"
src="${0%/*}"

install -d "$dest/etc/lighttpd/conf.d"
install -T "$src/lighttpd.conf" "$dest/etc/lighttpd/conf.d/turris-auth.conf"

install -d "$dest/usr/share/lighttpd-turris-auth/resources"
install -t "$dest/usr/share/lighttpd-turris-auth" \
	"$src/cgiauth.py" \
	"$src/login.html.j2" \
	"$src/magnet.lua"
install -t "$dest/usr/share/lighttpd-turris-auth/resources" \
	"$src/resources/app.css" \
	"$src/resources/favicon.ico" \
	"$src/resources/logo.svg"

install -d "$dest/etc/config"
if [ ! -f "$dest/etc/config/turris-auth" ]; then
	cat >"$dest/etc/config/turris-auth" <<-EOF
		config auth 'admin'
	EOF
fi

install -d "$dest/usr/bin"
install -t "$dest/usr/bin" \
	"$src/set-turris-auth"
