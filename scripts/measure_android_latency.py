"""Approximate acquisition-complete -> Android UI verification via USB restart.

This includes manual-refresh-equivalent app startup and ADB inspection overhead.
It is one observed sample, not a polling or cloud latency benchmark.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET
import serial
from mqtt_bridge import request


def run(args):
    adb = [str(args.adb)]
    report = dict(at=datetime.now(timezone.utc).isoformat(), passed=False,
                  scope=__doc__, device_id=args.device)
    deadline = time.monotonic() + 90
    sequence, began = None, None
    try:
        with serial.Serial(args.port, 115200, timeout=1) as wire:
            while time.monotonic() < deadline:
                line = wire.readline().decode('utf-8', errors='replace').strip()
                acquired = re.match(r'SAMPLE sequence=(\d+) uptime_ms=(\d+)', line)
                if acquired:
                    sequence = int(acquired.group(1))
                    began = time.monotonic()
                    report.update(sequence=sequence, acquisition_complete_seen_at=datetime.now(timezone.utc).isoformat())
                if sequence is not None and line.startswith(f'STORED sequence={sequence} '):
                    report['acquisition_complete_to_ack_ms'] = round((time.monotonic()-began)*1000, 2)
                    break
            else:
                raise RuntimeError('No fresh sample and persistence ACK observed')
        code, rows = request(args.api, 'GET', f'/api/measurements?device_id={args.device}&limit=20')
        row = next((r for r in rows if r['sequence'] == sequence), None) if code == 200 else None
        if not row:
            raise RuntimeError('Observed sequence missing from API')
        # Phone is configured to the same local timezone and Spanish date format.
        received = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')).astimezone()
        months = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        expected_date = f"Recibido {received.day:02d} {months[received.month-1]} {received.year} · {received:%H:%M:%S}"
        subprocess.run(adb+['shell','am','force-stop','com.hydromate.mobile'], check=True, capture_output=True)
        subprocess.run(adb+['shell','am','start','-n','com.hydromate.mobile/.MainActivity'], check=True, capture_output=True)
        local_xml = Path('.local/android-latency.xml')
        while time.monotonic() < deadline:
            try:
                subprocess.run(adb+['shell','uiautomator','dump','/sdcard/hydromate-latency.xml'], check=True, capture_output=True, timeout=20)
                subprocess.run(adb+['pull','/sdcard/hydromate-latency.xml',str(local_xml)], check=True, capture_output=True, timeout=10)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                report['ui_inspection_retries'] = report.get('ui_inspection_retries', 0) + 1
                time.sleep(.5)
                continue
            texts = [n.get('text','') for n in ET.parse(local_xml).iter('node') if n.get('package') == 'com.hydromate.mobile']
            if expected_date in texts and any('TDS simulado' in t for t in texts):
                report.update(passed=True, expected_received_label=expected_date,
                              acquisition_complete_to_ui_verified_ms=round((time.monotonic()-began)*1000,2),
                              ui_verified_at=datetime.now(timezone.utc).isoformat(), api_measurement=row)
                break
            time.sleep(.5)
        if not report['passed']:
            raise RuntimeError('Expected new timestamp not observed in Android UI')
    except Exception as error:
        report['error'] = str(error)
    finally:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
        print(json.dumps(dict(passed=report['passed'],output=str(args.output),
                              elapsed_ms=report.get('acquisition_complete_to_ui_verified_ms'))),flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True)
    p.add_argument('--adb',type=Path,required=True)
    p.add_argument('--device',default='hydromate-01')
    p.add_argument('--api',default='http://127.0.0.1:8000')
    p.add_argument('--output',type=Path,required=True)
    run(p.parse_args())
