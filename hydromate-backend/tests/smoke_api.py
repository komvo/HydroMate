"""Non-destructive HTTP smoke test. Leaves synthetic records under a unique device_id."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

def run(base_url, output):
    device = 'test-api-' + uuid.uuid4().hex[:12]
    events = []
    sample = dict(device_id=device, sequence=1, sample_number=1, reason=['synthetic_test'],
                  temperature_c=24.3, light_pct=65.2, light_state='MEDIA',
                  water_level_pct=82.4, water_level_state='LLENO', ph=6.2, tds_ppm=650)

    def request(method, path, payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(base_url + path, data=body, method=method,
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        start = time.perf_counter()
        try:
            response = urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            data = json.load(response)
            result = dict(method=method, path=path, sequence=(payload or {}).get('sequence'),
                          status=response.status, elapsed_ms=round((time.perf_counter()-start)*1000,2))
        events.append(result)
        return result['status'], data

    success = False
    try:
        for seq in range(1,11):
            status, data = request('POST','/api/measurements',sample | {'sequence':seq})
            assert status == 201, (seq,status)
            assert data['measurement']['device_id'] == device
        status, _ = request('POST','/api/measurements',sample | {'sequence':11,'ph':50})
        assert status == 422
        status, _ = request('POST','/api/measurements',sample)
        assert status == 409
        # Two competing clients: exactly one new row and one conflict are required.
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:request('POST','/api/measurements',sample | {'sequence':12}),range(2)))
        assert sorted(x[0] for x in results)==[201,409]
        query=urllib.parse.urlencode({'device_id':device,'limit':100})
        status, history=request('GET','/api/measurements?'+query)
        assert status==200 and len(history)==11
        assert {x['sequence'] for x in history}==set(range(1,11)) | {12}
        status, latest=request('GET','/api/measurements/latest?device_id='+device)
        assert status==200 and latest['sequence']==12
        status,_=request('GET','/api/measurements/latest?device_id='+device+'-absent')
        assert status==404
        success=True
    finally:
        report=dict(timestamp=datetime.now(timezone.utc).isoformat(),device_id=device,
                    synthetic=True,passed=success,latency_scope='HTTP client to API response',events=events)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps({'passed':success,'device_id':device,'report':str(output)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8000')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(args.base_url.rstrip('/'),args.output)
