<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Measurement extends Model
{
    protected $fillable = [
        'device_id',
        'message_version',
        'light_lux',
        'water_present',
        'sources',
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
        'sources' => 'array',
        'message_version' => 'integer',
        'light_lux' => 'float',
        'water_present' => 'boolean',

        'temperature_c' => 'float',
        'light_pct' => 'float',
        'water_level_pct' => 'float',
        'ph' => 'float',
        'tds_ppm' => 'float',
    ];
}
