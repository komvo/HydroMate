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
        $version = $this->input('message_version');
        $physical = in_array($version, [2, 3], true);
        $v3 = $version === 3;
        $sourceKeys = ['temperature_c', 'light_lux', 'water_present', 'ph', 'tds_ppm'];
        if ($v3) {
            $sourceKeys[] = 'ec_us_cm';
        }
        $sensor = fn ($min, $max) => [$v3 ? 'present' : 'required', ...($v3 ? ['nullable'] : []),
            'numeric', "between:$min,$max"];

        return [
            'message_version' => ['sometimes', 'required', function ($attribute, $value, $fail) {
                if (! in_array($value, [2, 3], true)) {
                    $fail('message_version debe ser el entero JSON 2 o 3.');
                }
            }],
            'device_id' => ['required', 'string', 'max:64'],
            'sequence' => ['required', 'integer', 'min:1', 'max:9223372036854775807'],
            'sample_number' => ['nullable', 'integer', 'min:1', 'max:9223372036854775807'],
            'reason' => ['nullable', 'array', 'list', 'max:10'],
            'reason.*' => ['required', 'string', 'max:64'],
            'temperature_c' => $sensor(0, 50),
            'light_pct' => [$physical ? 'prohibited' : 'required', 'numeric', 'between:0,100'],
            'light_state' => [$physical ? 'prohibited' : 'required', 'in:BAJA,MEDIA,ALTA'],
            'water_level_pct' => [$physical ? 'prohibited' : 'required', 'numeric', 'between:0,100'],
            'water_level_state' => [$physical ? 'prohibited' : 'required', 'in:VACIO,MEDIO,LLENO'],
            'light_lux' => $physical ? $sensor(0, 100000) : ['prohibited'],
            'water_present' => [$physical ? ($v3 ? 'present' : 'required') : 'prohibited', ...($v3 ? ['nullable'] : []), function ($attribute, $value, $fail) {
                if (! is_bool($value)) {
                    $fail('water_present debe ser un booleano JSON.');
                }
            }],
            'sources' => [$physical ? 'required' : 'prohibited', 'array:'.implode(',', $sourceKeys)],
            'ph' => $sensor(0, 14),
            'tds_ppm' => $sensor(0, 1000),
            'ec_us_cm' => $v3 ? $sensor(0, 100000) : ['prohibited'],
            'captured_at' => $v3 ? ['sometimes', 'nullable', 'date_format:Y-m-d\TH:i:s\Z', 'before_or_equal:'.now()->addMinute()->format('Y-m-d\TH:i:s\Z')] : ['prohibited'],
        ] + array_combine(array_map(fn ($key) => 'sources.'.$key, $sourceKeys),
            array_fill(0, count($sourceKeys), [$physical ? 'required' : 'prohibited',
                $v3 ? 'in:real,simulated,unavailable,invalid' : 'in:real,simulated']));
    }

    public function after(): array
    {
        if ($this->input('message_version') !== 3) {
            return [];
        }
        return [function ($validator) {
            foreach (['temperature_c', 'light_lux', 'water_present', 'ph', 'tds_ppm', 'ec_us_cm'] as $key) {
                $value = $this->input($key);
                $source = $this->input('sources.'.$key);
                if (in_array($source, ['unavailable', 'invalid'], true) && $value !== null) {
                    $validator->errors()->add($key, 'Un sensor no disponible o inválido debe enviar null.');
                }
                if (in_array($source, ['real', 'simulated'], true) && $value === null) {
                    $validator->errors()->add($key, 'Un origen real o simulado requiere un valor.');
                }
                if ($value !== null && $key !== 'water_present' && (! is_int($value) && ! is_float($value))) {
                    $validator->errors()->add($key, 'Debe ser un número JSON, no una cadena.');
                }
                if ($key !== 'water_present' && (is_int($value) || is_float($value))
                    && abs($value - round($value, 2)) > 0.0000001) {
                    $validator->errors()->add($key, 'Enviar como máximo dos decimales para conservar el valor sin redondeo al persistir.');
                }
            }
        }];
    }
}
