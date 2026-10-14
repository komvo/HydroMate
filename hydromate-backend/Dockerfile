# syntax=docker/dockerfile:1
FROM php:8.4-apache-bookworm AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev libonig-dev libzip-dev unzip \
    && docker-php-ext-install -j2 pdo_pgsql mbstring zip opcache \
    && a2enmod rewrite \
    && rm -rf /var/lib/apt/lists/*

FROM runtime AS dependencies
COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer
WORKDIR /var/www/html
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --no-interaction --prefer-dist --no-progress
COPY . .
RUN composer dump-autoload --no-dev --classmap-authoritative --no-scripts \
    && mkdir -p bootstrap/cache storage/framework/cache/data storage/framework/sessions storage/framework/views storage/logs \
    && php artisan package:discover --ansi

FROM runtime AS production
WORKDIR /var/www/html
COPY --from=dependencies /var/www/html /var/www/html
COPY docker/apache.conf /etc/apache2/sites-available/000-default.conf
COPY docker/php-production.ini /usr/local/etc/php/conf.d/hydromate-production.ini
COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/hydromate-entrypoint
COPY docker/healthcheck.php /usr/local/bin/hydromate-healthcheck.php
RUN printf 'Listen 8080\n' > /etc/apache2/ports.conf \
    && printf 'ServerName localhost\n' > /etc/apache2/conf-available/server-name.conf \
    && a2enconf server-name \
    && mkdir -p storage/framework/cache/data storage/framework/sessions storage/framework/views storage/logs \
    && chown -R www-data:www-data storage bootstrap/cache /var/run/apache2 /var/lock/apache2 /var/log/apache2
ENV APP_ENV=production APP_DEBUG=false LOG_CHANNEL=stderr
USER www-data
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["php", "/usr/local/bin/hydromate-healthcheck.php"]
ENTRYPOINT ["hydromate-entrypoint"]
CMD ["apache2-foreground"]
