"""Capture ESP32 serial samples and persistence ACKs; verify the same rows through API."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
import urllib.parse
import serial
from mqtt_bridge import request


def run(args):
    events, samples, stored = [], {}, set()
    sample_uptime = {}
    began = time.monotonic()
    passed = False
    try:
        with serial.Serial(args.port, 115200, timeout=1) as wire:
            # Opening serial can reset the ESP32; sequence reservation handles this.
            while time.monotonic()-began < args.duration and len(stored.intersection(samples)) < args.target:
                line = wire.readline().decode('utf-8', errors='replace').strip()
                if not line:
                    continue
                now = datetime.now(timezone.utc).isoformat()
                if line.startswith('{'):
                    try:
                        sample = json.loads(line)
                        if sample.get('device_id') == args.device:
                            samples[sample['sequence']] = sample
                            events.append(dict(at=now, event='sample_serial', payload=sample))
                            print(f"SAMPLE {sample['sequence']}", flush=True)
                    except (ValueError, AttributeError):
                        pass
                elif line.startswith(('SAMPLE ', 'RESTORED ', 'SEND ', 'STORED ', 'SENSOR_INVALID ', 'HALT:', 'MQTT_', 'WIFI_')):
                    events.append(dict(at=now, event='firmware_log', detail=line))
                    print(line, flush=True)
                    acquisition = re.match(r'SAMPLE sequence=(\d+) uptime_ms=(\d+)', line)
                    if acquisition:
                        sample_uptime[int(acquisition.group(1))] = int(acquisition.group(2))
                    match = re.match(r'STORED sequence=(\d+)', line)
                    if match:
                        seq=int(match.group(1))
                        stored.add(seq)
                        confirmation=re.match(r'STORED sequence=\d+ uptime_ms=(\d+)',line)
                        if confirmation and seq in sample_uptime:
                            events.append(dict(event='firmware_acquisition_end_to_persistence_ack',sequence=seq,
                                               elapsed_ms=(int(confirmation.group(1))-sample_uptime[seq]) & 0xffffffff))
            code, rows = request(args.api, 'GET', '/api/measurements?' + urllib.parse.urlencode(dict(device_id=args.device,limit=100)))
            found = {r['sequence']:r for r in rows} if code == 200 else {}
            verified = []
            for seq in sorted(stored):
                source = samples.get(seq)
                row = found.get(seq)
                if source and row and all(row.get(k) == v for k,v in source.items()):
                    verified.append(seq)
            passed = len(verified) >= args.target
            events.append(dict(event='api_verification', status=code, verified_sequences=verified,
                               stored_sequences=sorted(stored), serial_sample_sequences=sorted(samples)))
    finally:
        report = dict(at=datetime.now(timezone.utc).isoformat(), device_id=args.device, passed=passed,
                      target=args.target, duration_seconds=round(time.monotonic()-began,2),
                      scope='Physical firmware declares four real variables, TDS simulated; serial samples/ACK compared to API; frontend latency and calibration not measured', events=events)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(dict(passed=passed, output=str(args.output))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True)
    p.add_argument('--device',default='hydromate-01')
    p.add_argument('--api',default='http://127.0.0.1:8000')
    p.add_argument('--duration',type=float,default=420)
    p.add_argument('--target',type=int,default=10)
    p.add_argument('--output',type=Path,required=True)
    run(p.parse_args())
