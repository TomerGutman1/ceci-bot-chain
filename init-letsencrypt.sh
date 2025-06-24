#!/bin/bash
# init-letsencrypt.sh - Initialize SSL certificates

if ! [ -x "$(command -v docker compose)" ]; then
  echo 'Error: docker compose is not installed.' >&2
  exit 1
fi

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

if [ -z "$DOMAIN_NAME" ] || [ -z "$ADMIN_EMAIL" ]; then
  echo "Error: DOMAIN_NAME and ADMIN_EMAIL must be set in .env file"
  exit 1
fi

domains=($DOMAIN_NAME)
rsa_key_size=4096
data_path="./certbot"
staging=0 # Set to 1 for testing

echo "### Creating required directories..."
mkdir -p "$data_path/conf"
mkdir -p "$data_path/www"

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
fi

echo "### Creating dummy certificate for $domains..."
path="/etc/letsencrypt/live/$domains"
mkdir -p "$data_path/conf/live/$domains"
docker run --rm -v "$PWD/$data_path/conf:/etc/letsencrypt" \
  -v "$PWD/$data_path/www:/var/www/certbot" \
  --entrypoint "/bin/sh" certbot/certbot \
  -c "openssl req -x509 -nodes -newkey rsa:1024 -days 1 \
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'"

echo "### Starting nginx..."
docker compose up -d nginx

echo "### Deleting dummy certificate for $domains..."
docker run --rm -v "$PWD/$data_path/conf:/etc/letsencrypt" \
  -v "$PWD/$data_path/www:/var/www/certbot" \
  --entrypoint "/bin/sh" certbot/certbot \
  -c "rm -rf /etc/letsencrypt/live/$domains && \
      rm -rf /etc/letsencrypt/archive/$domains && \
      rm -rf /etc/letsencrypt/renewal/$domains.conf"

echo "### Requesting Let's Encrypt certificate for $domains..."
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

staging_arg=""
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker run --rm -v "$PWD/$data_path/conf:/etc/letsencrypt" \
  -v "$PWD/$data_path/www:/var/www/certbot" \
  --entrypoint "/bin/sh" certbot/certbot \
  -c "certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $domain_args \
    --email $ADMIN_EMAIL \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --non-interactive \
    --force-renewal"

echo "### Reloading nginx..."
docker compose exec nginx nginx -s reload
