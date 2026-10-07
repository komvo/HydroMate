<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class MeasurementApiTest extends TestCase
{
    use RefreshDatabase {
        refreshDatabase as private refreshIsolatedTestDatabase;
    }

    public function refreshDatabase(): void
    {
        // Never let this suite reset the user's PostgreSQL database.
        if (config('database.default') !== 'sqlite'
            || config('database.connections.sqlite.database') !== ':memory:') {
            throw new \RuntimeException('Tests require SQLite :memory:. PostgreSQL must not be reset.');
        }
        $this->refreshIsolatedTestDatabase();
    }

    private function payload(array $changes = []): array
    {
        return array_replace([
            'device_id' => 'test-tower-a', 'sequence' => 1, 'sample_number' => 1,
            'reason' => ['test'], 'temperature_c' => 24.3, 'light_pct' => 65.2,
            'light_state' => 'MEDIA', 'water_level_pct' => 82.4,
            'water_level_state' => 'LLENO', 'ph' => 6.2, 'tds_ppm' => 650,
        ], $changes);
    }

    public function test_measurements_are_stored_and_returned_by_device_in_deterministic_order(): void
    {
        $this->freezeTime();
        for ($sequence = 1; $sequence <= 10; $sequence++) {
            $this->postJson('/api/measurements', $this->payload(['sequence' => $sequence]))
                ->assertCreated()->assertJsonPath('measurement.sequence', $sequence);
        }
        $this->postJson('/api/measurements', $this->payload(['device_id' => 'test-tower-b']))
            ->assertCreated();
        $this->assertDatabaseCount('measurements', 11);
        $this->getJson('/api/measurements?device_id=test-tower-a&limit=3')
            ->assertOk()->assertJsonCount(3)
            ->assertJsonPath('0.sequence', 10)->assertJsonPath('2.sequence', 8);
        $this->getJson('/api/measurements/latest?device_id=test-tower-a')
            ->assertOk()->assertJsonPath('sequence', 10)
            ->assertJsonPath('device_id', 'test-tower-a');
    }

    public function test_duplicate_is_rejected_by_database_constraint_without_changing_original(): void
    {
        $this->postJson('/api/measurements', $this->payload())->assertCreated();
        $this->postJson('/api/measurements', $this->payload(['ph' => 7]))
            ->assertConflict()->assertJsonPath('message', 'Medicion duplicada');
        $this->assertDatabaseCount('measurements', 1);
        $this->assertDatabaseHas('measurements', ['device_id' => 'test-tower-a', 'ph' => 6.2]);
    }

    #[DataProvider('invalidMeasurements')]
    public function test_invalid_measurement_never_reaches_database(string $field, mixed $value): void
    {
        $this->postJson('/api/measurements', $this->payload([$field => $value]))
            ->assertUnprocessable()->assertJsonValidationErrors($field);
        $this->assertDatabaseCount('measurements', 0);
    }

    public static function invalidMeasurements(): array
    {
        return [
            'invalid pH' => ['ph', 50],
            'missing device' => ['device_id', ''],
            'negative sequence' => ['sequence', -1],
            'integer overflow' => ['sequence', '9223372036854775808'],
            'invalid water level' => ['water_level_pct', 101],
            'invalid light state' => ['light_state', 'UNKNOWN'],
            'reason is not a list' => ['reason', ['key' => 'startup']],
            'too many reasons' => ['reason', array_fill(0, 11, 'startup')],
        ];
    }

    public function test_nested_reason_is_rejected(): void
    {
        $this->postJson('/api/measurements', $this->payload(['reason' => [['nested']]]))
            ->assertUnprocessable()->assertJsonValidationErrors('reason.0');
        $this->assertDatabaseCount('measurements', 0);
    }

    public function test_empty_device_has_no_history_and_no_latest_measurement(): void
    {
        $this->postJson('/api/measurements', $this->payload())->assertCreated();
        $this->getJson('/api/measurements?device_id=other')->assertOk()->assertExactJson([]);
        $this->getJson('/api/measurements/latest?device_id=other')->assertNotFound();
    }

    public function test_invalid_query_returns_json_validation_error(): void
    {
        $this->getJson('/api/measurements?limit=101')->assertUnprocessable();
        $this->getJson('/api/measurements?device_id[]=test')->assertUnprocessable();
        $this->getJson('/api/measurements/latest?device_id=')->assertUnprocessable();
    }

    public function test_documented_producer_fixture_round_trips_and_retries_without_duplicate(): void
    {
        $payload = json_decode(file_get_contents(__DIR__.'/../Fixtures/telemetry/valid.json'), true, 512, JSON_THROW_ON_ERROR);
        $this->postJson('/api/measurements', $payload)->assertCreated();
        $this->postJson('/api/measurements', $payload)->assertConflict();
        $response = $this->getJson('/api/measurements/latest?device_id='.$payload['device_id'])->assertOk();
        foreach ($payload as $field => $value) {
            $this->assertEquals($value, $response->json($field));
        }
        $response->assertJsonStructure(['id', 'created_at', 'updated_at']);
        $this->assertDatabaseCount('measurements', 1);
    }

    public function test_documented_invalid_and_missing_sensor_fixtures_are_not_stored(): void
    {
        foreach (['invalid-ph.json', 'unavailable-sensor.json'] as $fixture) {
            $payload = json_decode(file_get_contents(__DIR__.'/../Fixtures/telemetry/'.$fixture), true, 512, JSON_THROW_ON_ERROR);
            $this->postJson('/api/measurements', $payload)
                ->assertUnprocessable()->assertJsonValidationErrors('ph');
        }
        $this->assertDatabaseCount('measurements', 0);
    }
}
