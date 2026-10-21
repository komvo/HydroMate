<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\MeasurementController;
use App\Http\Controllers\Api\SampleRequestController;

Route::post('/devices/{deviceId}/measurement-requests', [SampleRequestController::class, 'create'])
    ->where('deviceId', '[A-Za-z0-9_-]{1,64}')->middleware('throttle:12,1');
Route::get('/measurement-requests/{requestId}', [SampleRequestController::class, 'show'])->whereUuid('requestId');
Route::get('/internal/measurement-requests', [SampleRequestController::class, 'pending']);

Route::get('/devices/{deviceId}/status', [MeasurementController::class, 'status'])
    ->where('deviceId', '[A-Za-z0-9_-]{1,64}');

Route::post(
    '/measurements',
    [MeasurementController::class, 'store']
);

Route::get(
    '/measurements',
    [MeasurementController::class, 'index']
);

Route::get(
    '/measurements/latest',
    [MeasurementController::class, 'latest']
);
