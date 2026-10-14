<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\MeasurementController;

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
