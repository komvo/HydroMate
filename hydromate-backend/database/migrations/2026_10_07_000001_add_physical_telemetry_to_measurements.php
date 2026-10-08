<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('measurements', function (Blueprint $table) {
            $table->unsignedSmallInteger('message_version')->nullable();
            $table->decimal('light_lux', 10, 2)->nullable();
            $table->boolean('water_present')->nullable();
            $table->json('sources')->nullable();
            $table->decimal('light_pct', 5, 2)->nullable()->change();
            $table->string('light_state', 10)->nullable()->change();
            $table->decimal('water_level_pct', 5, 2)->nullable()->change();
            $table->string('water_level_state', 10)->nullable()->change();
        });
    }

    public function down(): void
    {
        // Reverting would invalidate v2 rows. Require an explicit data migration.
        throw new RuntimeException('No revertir sin respaldar y migrar las mediciones v2.');
    }
};
