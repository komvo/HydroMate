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
        $v2 = $this->input('message_version') === 2;

        return [
            'message_version' => ['sometimes', 'required', function ($attribute, $value, $fail) {
                if ($value !== 2) {
                    $fail('message_version debe ser el entero JSON 2.');
                }
            }],
            'device_id' => ['required', 'string', 'max:64'],
            'sequence' => ['required', 'integer', 'min:1', 'max:9223372036854775807'],
            'sample_number' => ['nullable', 'integer', 'min:1', 'max:9223372036854775807'],
            'reason' => ['nullable', 'array', 'list', 'max:10'],
            'reason.*' => ['required', 'string', 'max:64'],
            'temperature_c' => ['required', 'numeric', 'between:0,50'],
            'light_pct' => [$v2 ? 'prohibited' : 'required', 'numeric', 'between:0,100'],
            'light_state' => [$v2 ? 'prohibited' : 'required', 'in:BAJA,MEDIA,ALTA'],
            'water_level_pct' => [$v2 ? 'prohibited' : 'required', 'numeric', 'between:0,100'],
            'water_level_state' => [$v2 ? 'prohibited' : 'required', 'in:VACIO,MEDIO,LLENO'],
            'light_lux' => [$v2 ? 'required' : 'prohibited', 'numeric', 'between:0,100000'],
            'water_present' => [$v2 ? 'required' : 'prohibited', function ($attribute, $value, $fail) {
                if (! is_bool($value)) {
                    $fail('water_present debe ser un booleano JSON.');
                }
            }],
            'sources' => [$v2 ? 'required' : 'prohibited', 'array:temperature_c,light_lux,water_present,ph,tds_ppm'],
            'sources.temperature_c' => [$v2 ? 'required' : 'prohibited', 'in:real,simulated'],
            'sources.light_lux' => [$v2 ? 'required' : 'prohibited', 'in:real,simulated'],
            'sources.water_present' => [$v2 ? 'required' : 'prohibited', 'in:real,simulated'],
            'sources.ph' => [$v2 ? 'required' : 'prohibited', 'in:real,simulated'],
            'sources.tds_ppm' => [$v2 ? 'required' : 'prohibited', 'in:real,simulated'],
            'ph' => ['required', 'numeric', 'between:0,14'],
            'tds_ppm' => ['required', 'numeric', 'between:0,1000'],
        ];
    }
}
