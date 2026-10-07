<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('measurements', function (Blueprint $table) {
            $table->id();

            $table->string('device_id', 64);

            $table->unsignedBigInteger('sequence');

            $table->unsignedBigInteger('sample_number')->nullable();

            $table->json('reason')->nullable();

            $table->decimal('temperature_c', 5, 2);

            $table->decimal('light_pct', 5, 2);

            $table->string('light_state', 10);

            $table->decimal('water_level_pct', 5, 2);

            $table->string('water_level_state', 10);

            $table->decimal('ph', 4, 2);

            $table->decimal('tds_ppm', 8, 2);

            $table->timestamps();

            $table->unique([
                'device_id',
                'sequence'
             ]);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('measurements');
    }
};
