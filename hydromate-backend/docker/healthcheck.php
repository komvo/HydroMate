<?php

// Boot/API + database connectivity. Does not insert data or require migrations.
try {
    $context = stream_context_create(['http' => ['timeout' => 3, 'ignore_errors' => true]]);
    $body = @file_get_contents('http://127.0.0.1:8080/up', false, $context);
    if ($body === false || ! preg_match('/^HTTP\/\S+ 200\b/', $http_response_header[0] ?? '')) {
        exit(1);
    }
    require '/var/www/html/vendor/autoload.php';
    $app = require '/var/www/html/bootstrap/app.php';
    $app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
    Illuminate\Support\Facades\DB::select('SELECT 1');
    exit(0);
} catch (Throwable $error) {
    // Keep credentials/connection details out of Docker health logs.
    exit(1);
}
