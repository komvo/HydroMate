<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\MeasurementController;

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