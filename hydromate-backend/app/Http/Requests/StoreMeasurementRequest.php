<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreMeasurementRequest extends FormRequest
{
    public function authorize(): bool
    {
        // Local development API; device authentication belongs to a later phase.
        return true;
    }

    public function rules(): array
    {
        return [
            'device_id' => ['required', 'string', 'max:64'],
            'sequence' => ['required', 'integer', 'min:1', 'max:9223372036854775807'],
            'sample_number' => ['nullable', 'integer', 'min:1', 'max:9223372036854775807'],
            'reason' => ['nullable', 'array', 'list', 'max:10'],
            'reason.*' => ['required', 'string', 'max:64'],
            'temperature_c' => ['required', 'numeric', 'between:0,50'],
            'light_pct' => ['required', 'numeric', 'between:0,100'],
            'light_state' => ['required', 'in:BAJA,MEDIA,ALTA'],
            'water_level_pct' => ['required', 'numeric', 'between:0,100'],
            'water_level_state' => ['required', 'in:VACIO,MEDIO,LLENO'],
            'ph' => ['required', 'numeric', 'between:0,14'],
            'tds_ppm' => ['required', 'numeric', 'between:0,1000'],
        ];
    }
}
