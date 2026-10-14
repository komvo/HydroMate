<?php

return [
    // Receipt/acquisition freshness, not proof of a live socket or sensor authenticity.
    'freshness_seconds' => min(86400, max(1, (int) env('TELEMETRY_FRESHNESS_SECONDS', 120))),
];
