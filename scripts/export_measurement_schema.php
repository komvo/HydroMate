<?php

// Read-only schema evidence; never exports credentials or actual measurement rows.
require __DIR__.'/../hydromate-backend/vendor/autoload.php';
$app = require __DIR__.'/../hydromate-backend/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
if (config('database.default') !== 'pgsql') {
    throw new RuntimeException('Expected PostgreSQL connection.');
}
$columns = Illuminate\Support\Facades\DB::select(
    "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema='public' AND table_name='measurements' ORDER BY ordinal_position"
);
$constraints = Illuminate\Support\Facades\DB::select(
    "SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_schema='public' AND table_name='measurements'"
);
$output = $argv[1] ?? throw new RuntimeException('Provide output path.');
file_put_contents($output, json_encode(['at' => gmdate('c'), 'table' => 'measurements', 'columns' => $columns, 'constraints' => $constraints], JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR));
echo "Read-only PostgreSQL schema evidence exported.\n";
