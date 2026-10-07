<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Measurement extends Model
{
    protected $fillable = [
        'device_id',
        'sequence',
        'sample_number',
        'reason',
        'temperature_c',
        'light_pct',
        'light_state',
        'water_level_pct',
        'water_level_state',
        'ph',
        'tds_ppm',
    ];

    protected $casts = [
        'reason' => 'array',

        'temperature_c' => 'float',
        'light_pct' => 'float',
        'water_level_pct' => 'float',
        'ph' => 'float',
        'tds_ppm' => 'float',
    ];
}