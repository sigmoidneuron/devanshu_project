#!/usr/bin/env bash
set -euo pipefail
DOMAIN=$1
EMAIL=$2
WEBROOT=/var/www/certbot

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "Usage: $0 <domain> <email>"
  exit 1
fi

mkdir -p $WEBROOT
certbot certonly --webroot -w $WEBROOT -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
