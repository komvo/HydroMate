<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Measurement;
use Carbon\CarbonImmutable;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Str;

/** Short-lived requests to acquire telemetry; never arbitrary device commands. */
class SampleRequestController extends Controller
{
    public function create(Request $request, string $deviceId): JsonResponse
    {
        if ($request->all() !== []) {
            return response()->json(['message' => 'La solicitud de lectura no admite comandos ni parámetros.'], 422);
        }
        if (! Measurement::where('device_id', $deviceId)->exists() || str_starts_with($deviceId, 'test-')) {
            return response()->json(['message' => 'La torre todavía no tiene telemetría registrada.'], 404);
        }
        $item = Cache::lock('sample-request-lock:'.$deviceId, 3)->get(function () use ($deviceId) {
            $active = Cache::get('sample-request-device:'.$deviceId);
            if ($active && CarbonImmutable::parse($active['expires_at'])->isFuture() && ! $this->measurement($active)) {
                return $active;
            }
            $item = ['id' => (string) Str::uuid(), 'device_id' => $deviceId,
                'created_at' => now()->toISOString(), 'expires_at' => now()->addSeconds(30)->toISOString()];
            Cache::put('sample-request-device:'.$deviceId, $item, 90);
            Cache::put('sample-request-id:'.$item['id'], $item, 90);
            return $item;
        });
        if (! $item) {
            return response()->json(['message' => 'Hay otra solicitud en curso. Intenta de nuevo.'], 429);
        }
        return response()->json($item + ['state' => 'pending'], 202)->header('Cache-Control', 'no-store');
    }

    public function show(string $requestId): JsonResponse
    {
        $item = Cache::get('sample-request-id:'.$requestId);
        if (! $item) {
            return response()->json(['message' => 'La solicitud ya no está disponible.'], 404);
        }
        $measurement = $this->measurement($item);
        $state = $measurement ? 'stored' : (CarbonImmutable::parse($item['expires_at'])->isPast() ? 'expired' : 'pending');
        return response()->json($item + ['state' => $state, 'measurement' => $measurement])->header('Cache-Control', 'no-store');
    }

    // This route is reachable only inside the Docker application network.
    public function pending(): JsonResponse
    {
        $items = [];
        foreach (Measurement::select('device_id')->distinct()->where('device_id', 'not like', 'test-%')->limit(100)->pluck('device_id') as $device) {
            $item = Cache::get('sample-request-device:'.$device);
            if ($item && CarbonImmutable::parse($item['expires_at'])->isFuture() && ! $this->measurement($item)) {
                $items[] = $item;
            }
        }
        return response()->json($items)->header('Cache-Control', 'no-store');
    }

    private function measurement(array $item): ?Measurement
    {
        $query = Measurement::where('device_id', $item['device_id'])
            ->where('message_version', 3)->whereJsonContains('reason', 'request:'.$item['id'])
            ->where('created_at', '>=', CarbonImmutable::parse($item['created_at']))
            ->whereNotNull('captured_at')
            ->where('captured_at', '>=', CarbonImmutable::parse($item['created_at'])->startOfSecond())
            ->where('captured_at', '<=', CarbonImmutable::parse($item['expires_at']))
            ->whereJsonDoesntContain('reason', 'synthetic_test');
        foreach (['temperature_c', 'light_lux', 'water_present', 'ph', 'tds_ppm', 'ec_us_cm'] as $sensor) {
            $query->where('sources->'.$sensor, '!=', 'simulated');
        }
        return $query->orderBy('id')->first();
    }
}
