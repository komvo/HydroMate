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
        ]);

        return response()->json(
            $this->measurements($filters['device_id'] ?? null)
                ->limit($filters['limit'] ?? 20)
                ->get()
        );
    }

    public function latest(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'device_id' => ['sometimes', 'required', 'string', 'max:64'],
        ]);
        $measurement = $this->measurements($filters['device_id'] ?? null)->first();

        if (! $measurement) {
            return response()->json([
                'status' => 'error',
                'message' => 'No hay mediciones',
            ], 404);
        }

        return response()->json($measurement);
    }

    private function measurements(?string $deviceId): Builder
    {
        return Measurement::query()
            ->when($deviceId !== null, fn (Builder $query) => $query->where('device_id', $deviceId))
            ->orderByDesc('created_at')
            ->orderByDesc('id');
    }
}
