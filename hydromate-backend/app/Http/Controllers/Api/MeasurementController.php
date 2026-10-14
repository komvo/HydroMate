<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreMeasurementRequest;
use App\Models\Measurement;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\UniqueConstraintViolationException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class MeasurementController extends Controller
{
    public function store(StoreMeasurementRequest $request): JsonResponse
    {
        // The database constraint is authoritative even for simultaneous requests.
        try {
            $measurement = Measurement::create($request->validated());
        } catch (UniqueConstraintViolationException $exception) {
            if ($exception->index !== 'measurements_device_id_sequence_unique'
                && $exception->columns !== ['device_id', 'sequence']) {
                throw $exception;
            }

            return response()->json([
                'status' => 'error',
                'message' => 'Medicion duplicada',
            ], 409);
        }

        return response()->json([
            'status' => 'ok',
            'message' => 'Medicion registrada correctamente',
            'measurement' => $measurement,
        ], 201);
    }

    public function index(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'device_id' => ['sometimes', 'required', 'string', 'max:64'],
            'limit' => ['sometimes', 'required', 'integer', 'between:1,100'],
            'real_only' => ['sometimes', 'boolean'],
            'sequence' => ['sometimes', 'required', 'integer', 'min:1', 'max:9223372036854775807'],
        ]);

        return response()->json(
            $this->measurements($filters['device_id'] ?? null, (bool) ($filters['real_only'] ?? false))
                ->when(isset($filters['sequence']), fn (Builder $q) => $q->where('sequence', $filters['sequence']))
                ->limit($filters['limit'] ?? 20)
                ->get()
        )->header('X-HydroMate-Freshness-Seconds', (string) config('telemetry.freshness_seconds'));
    }

    public function latest(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'device_id' => ['sometimes', 'required', 'string', 'max:64'],
            'real_only' => ['sometimes', 'boolean'],
        ]);
        $measurement = $this->measurements($filters['device_id'] ?? null, (bool) ($filters['real_only'] ?? false))->first();

        if (! $measurement) {
            return response()->json([
                'status' => 'error',
                'message' => 'No hay mediciones',
            ], 404);
        }

        return response()->json($measurement);
    }

    public function status(Request $request, string $deviceId): JsonResponse
    {
        $filters = $request->validate(['real_only' => ['sometimes', 'boolean']]);
        $last = $this->measurements($deviceId, (bool) ($filters['real_only'] ?? false))->first();
        $threshold = config('telemetry.freshness_seconds');
        $age = $last ? max(0, now()->getTimestamp() - ($last->captured_at ?? $last->created_at)->getTimestamp(),
            now()->getTimestamp() - $last->created_at->getTimestamp()) : null;
        return response()->json([
            'device_id' => $deviceId,
            'state' => $last ? ($age > $threshold ? 'stale' : 'recent') : 'no_data',
            'freshness_seconds' => $threshold,
            'age_seconds' => $age,
            'last_sequence' => $last?->sequence,
            'last_received_at' => $last?->created_at,
            'last_captured_at' => $last?->captured_at,
            'basis' => 'telemetry_age_not_live_connection',
        ]);
    }

    private function measurements(?string $deviceId, bool $realOnly = false): Builder
    {
        $query = Measurement::query()
            ->when($deviceId !== null, fn (Builder $query) => $query->where('device_id', $deviceId))
            ->orderByDesc('created_at')
            ->orderByDesc('id');
        if ($realOnly) {
            $query->whereIn('message_version', [2, 3])->whereNotNull('sources')
                ->where('device_id', 'not like', 'test-%')
                ->where(fn (Builder $q) => $q->whereNull('reason')->orWhereJsonDoesntContain('reason', 'synthetic_test'));
            foreach (['temperature_c', 'light_lux', 'water_present', 'ph', 'tds_ppm'] as $key) {
                $query->where('sources->'.$key, '!=', 'simulated');
            }
            $query->where(fn (Builder $q) => $q->where('message_version', 2)->orWhere('sources->ec_us_cm', '!=', 'simulated'));
        }
        return $query;
    }
}
