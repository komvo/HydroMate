<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PartialTelemetryTest extends TestCase
{
    use RefreshDatabase {
        refreshDatabase as private refreshIsolated;
    }

    public function refreshDatabase(): void
    {
        if (config('database.default') !== 'sqlite' || config('database.connections.sqlite.database') !== ':memory:') {
            throw new \RuntimeException('Tests require isolated SQLite memory.');
        }
        $this->refreshIsolated();
    }

    private function payload(): array
    {
        return ['message_version' => 3, 'device_id' => 'hydromate-01', 'sequence' => 1,
            'temperature_c' => 24.3, 'light_lux' => 120.5, 'water_present' => false,
            'ph' => 6.2, 'tds_ppm' => null, 'ec_us_cm' => null, 'captured_at' => null,
            'sources' => ['temperature_c' => 'real', 'light_lux' => 'real', 'water_present' => 'real',
                'ph' => 'real', 'tds_ppm' => 'unavailable', 'ec_us_cm' => 'unavailable']];
    }

    public function test_partial_sensors_and_disconnected_tds_are_preserved_as_null(): void
    {
        $p = $this->payload();
        $p['ph'] = null;
        $p['sources']['ph'] = 'invalid';
        $this->postJson('/api/measurements', $p)->assertCreated()->assertJsonPath('measurement.ph', null)
            ->assertJsonPath('measurement.tds_ppm', null)->assertJsonPath('measurement.water_present', false);
        $this->getJson('/api/measurements?device_id=hydromate-01&real_only=1')->assertOk()->assertJsonCount(1);
    }

    public function test_provenance_value_disagreement_and_non_json_types_are_rejected(): void
    {
        $base = $this->payload();
        $cases = [$base + ['light_pct' => 10], array_replace($base, ['temperature_c' => '24.3']),
            array_replace($base, ['temperature_c' => 24.333]),
            array_replace($base, ['water_present' => 0]), array_replace($base, ['tds_ppm' => 650]),
            array_replace($base, ['ph' => null]), array_replace($base, ['message_version' => '3'])];
        $missing = $base;
        unset($missing['ec_us_cm']);
        $cases[] = $missing;
        foreach ($cases as $p) {
            $this->postJson('/api/measurements', $p)->assertUnprocessable();
        }
        $this->assertDatabaseCount('measurements', 0);
    }

    public function test_ec_has_its_own_unit_and_is_not_invented_from_tds(): void
    {
        $p = $this->payload();
        $p['ec_us_cm'] = 1200.5;
        $p['sources']['ec_us_cm'] = 'real';
        $this->postJson('/api/measurements', $p)->assertCreated()->assertJsonPath('measurement.ec_us_cm', 1200.5)
            ->assertJsonPath('measurement.tds_ppm', null);
    }

    public function test_real_only_excludes_simulation_even_under_the_physical_device_id(): void
    {
        $p = $this->payload();
        $this->postJson('/api/measurements', $p)->assertCreated();
        $p['sequence'] = 2;
        $p['temperature_c'] = 25.0;
        $p['sources']['temperature_c'] = 'simulated';
        $this->postJson('/api/measurements', $p)->assertCreated();
        $this->getJson('/api/measurements?device_id=hydromate-01')->assertJsonCount(2);
        $this->getJson('/api/measurements?device_id=hydromate-01&real_only=1')->assertJsonCount(1)->assertJsonPath('0.sequence', 1);
        $this->getJson('/api/measurements/latest?device_id=hydromate-01&real_only=1')->assertJsonPath('sequence', 1);
        $this->getJson('/api/measurements?device_id=hydromate-01&sequence=1&limit=1')->assertJsonCount(1)->assertJsonPath('0.sequence', 1);
        $p = $this->payload();
        $p['sequence'] = 3;
        $p['reason'] = ['synthetic_test'];
        $this->postJson('/api/measurements', $p)->assertCreated();
        $this->getJson('/api/measurements?device_id=hydromate-01&real_only=1')->assertJsonCount(1)->assertJsonPath('0.sequence', 1);
    }

    public function test_status_distinguishes_no_data_recent_and_stale_without_claiming_socket_state(): void
    {
        $this->freezeTime();
        $this->getJson('/api/devices/hydromate-01/status')->assertOk()->assertJsonPath('state', 'no_data');
        $this->postJson('/api/measurements', $this->payload())->assertCreated();
        $this->getJson('/api/devices/hydromate-01/status')->assertJsonPath('state', 'recent')->assertJsonPath('last_sequence', 1);
        $this->travel(3)->minutes();
        $this->getJson('/api/devices/hydromate-01/status')->assertJsonPath('state', 'stale');
    }

    public function test_delayed_acquisition_is_stale_even_with_a_new_receipt_and_future_time_is_rejected(): void
    {
        $this->freezeTime();
        $p = $this->payload();
        $p['captured_at'] = now()->subMinutes(5)->format('Y-m-d\TH:i:s\Z');
        $this->postJson('/api/measurements', $p)->assertCreated();
        $this->getJson('/api/devices/hydromate-01/status')->assertJsonPath('state', 'stale');
        $p['sequence'] = 2;
        $p['captured_at'] = now()->addMinutes(5)->format('Y-m-d\TH:i:s\Z');
        $this->postJson('/api/measurements', $p)->assertUnprocessable();
        $this->assertDatabaseCount('measurements', 1);
    }
}
