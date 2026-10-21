<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Cache;
use Tests\TestCase;

class SampleRequestTest extends TestCase
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

    protected function setUp(): void
    {
        parent::setUp();
        Cache::flush();
    }

    private function measurement(int $sequence, array $reason = []): array
    {
        return ['message_version' => 3, 'device_id' => 'hydromate-01', 'sequence' => $sequence,
            'reason' => $reason, 'captured_at' => now()->format('Y-m-d\TH:i:s\Z'),
            'temperature_c' => null, 'light_lux' => 200.0, 'water_present' => true,
            'ph' => 6.2, 'tds_ppm' => 500.0, 'ec_us_cm' => null,
            'sources' => ['temperature_c' => 'invalid', 'light_lux' => 'real', 'water_present' => 'real',
                'ph' => 'real', 'tds_ppm' => 'real', 'ec_us_cm' => 'unavailable']];
    }

    private function requestSample(): array
    {
        return $this->postJson('/api/devices/hydromate-01/measurement-requests', [])
            ->assertStatus(202)->assertJsonPath('state', 'pending')->json();
    }

    public function test_only_correlated_new_acquisition_completes_request(): void
    {
        $this->postJson('/api/measurements', $this->measurement(1))->assertCreated();
        $request = $this->requestSample();
        $this->postJson('/api/measurements', $this->measurement(2))->assertCreated();
        $url = '/api/measurement-requests/'.$request['id'];
        $this->getJson($url)->assertOk()->assertJsonPath('state', 'pending');
        $this->getJson('/api/internal/measurement-requests')->assertOk()->assertJsonCount(1);
        $this->postJson('/api/measurements', $this->measurement(3, ['requested', 'request:'.$request['id']]))->assertCreated();
        $this->getJson($url)->assertOk()->assertJsonPath('state', 'stored')->assertJsonPath('measurement.sequence', 3);
        $this->getJson('/api/internal/measurement-requests')->assertOk()->assertJsonCount(0);
        $this->assertNotSame($request['id'], $this->requestSample()['id']);
    }

    public function test_duplicate_clicks_share_pending_request_and_expiry_never_returns_old_measurement(): void
    {
        $this->postJson('/api/measurements', $this->measurement(1))->assertCreated();
        $request = $this->requestSample();
        $this->assertSame($request['id'], $this->requestSample()['id']);
        $this->travel(31)->seconds();
        $this->getJson('/api/measurement-requests/'.$request['id'])->assertOk()->assertJsonPath('state', 'expired')
            ->assertJsonPath('measurement', null);
        $this->getJson('/api/internal/measurement-requests')->assertOk()->assertJsonCount(0);
    }

    public function test_unknown_devices_and_arbitrary_commands_are_not_accepted(): void
    {
        $this->postJson('/api/devices/unknown/measurement-requests', [])->assertNotFound();
        $this->postJson('/api/measurements', $this->measurement(1))->assertCreated();
        $this->postJson('/api/devices/hydromate-01/measurement-requests', ['action' => 'pump_on'])->assertUnprocessable();
    }

    public function test_reading_with_a_matching_marker_but_old_acquisition_is_not_a_fresh_response(): void
    {
        $this->postJson('/api/measurements', $this->measurement(1))->assertCreated();
        $request = $this->requestSample();
        $old = $this->measurement(2, ['request:'.$request['id']]);
        $old['captured_at'] = now()->subMinute()->format('Y-m-d\TH:i:s\Z');
        $this->postJson('/api/measurements', $old)->assertCreated();
        $this->getJson('/api/measurement-requests/'.$request['id'])->assertOk()->assertJsonPath('state', 'pending');
    }
}
