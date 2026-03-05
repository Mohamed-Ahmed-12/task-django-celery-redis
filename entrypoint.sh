#!/bin/sh

set -e

echo "🚀 Starting entrypoint script..."

wait_for_db() {
    echo "⏳ Waiting for database..."
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 1
    done
    echo "✅ Database ready!"
}

wait_for_redis() {
    echo "⏳ Waiting for Redis..."
    while ! nc -z redis 6379; do
        sleep 1
    done
    echo "✅ Redis ready!"
}

wait_for_db
wait_for_redis

cd /app/src

# Create the directory at runtime so chmod has a target
mkdir -p /app/src/staticfiles

if [ "$1" = "gunicorn" ]; then
    echo "🔓 Adjusting static file permissions..."
    chmod -R 777 /app/src/staticfiles

    echo "📦 Applying migrations..."
    python manage.py migrate --noinput

    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput

    echo "👤 Checking superuser..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created')
EOF
fi

echo "🎯 Executing: $@"
exec "$@"