<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('measurements', function (Blueprint $table) {
            $table->decimal('temperature_c', 5, 2)->nullable()->change();
            $table->decimal('ph', 4, 2)->nullable()->change();
            $table->decimal('tds_ppm', 8, 2)->nullable()->change();
            $table->decimal('ec_us_cm', 10, 2)->nullable();
            $table->timestampTz('captured_at')->nullable();
        });
    }

    public function down(): void
    {
        throw new RuntimeException('Respaldar y reconciliar filas v3 antes de revertir esta migración.');
    }
};
