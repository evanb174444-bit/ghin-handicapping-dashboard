"""Split the Trials/GPS/Challenges CSV envelopes without changing their values.

Example: python3 scripts/unpack_dashboard_bundles.py --output /tmp/unpacked trials.csv gps.csv challenges.csv
Creates a NEW output directory. Does not install or publish dashboard data.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ALLOWED = {
    'trial_monthly_history', 'trial_cohorts', 'current_trial_pools',
    'ytd_trial_destinations', 'gps_active_reconciliation', 'gps_monthly_activity',
    'gps_subscriber_tenure_revised', 'gps_active_auto_renew_status',
    'ghin_challenges', 'challenge_course_names',
    'trial_conversion_timing', 'trial_conversion_timing_exceptions',
    'trial_conversion_source_exceptions', 'cumulative_trial_destination_associations',
    'trial_conversion_reconciliation',
}

def unpack(sources, output):
    output.mkdir(parents=True, exist_ok=False)
    csv.field_size_limit(16 * 1024 * 1024)
    handles, writers, columns = {}, {}, {}
    counts = Counter()
    manifests = set()
    metadata = {}
    def cell(value):
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, (dict, list)):
            return json.dumps(value, separators=(',', ':'))
        return value
    try:
        for source in sources:
            with source.open(encoding='utf-8-sig', newline='') as handle:
                reader = csv.DictReader(handle)
                required = {'dataset', 'record_type', 'extracted_at', 'source_database', 'reporting_timezone', 'row_data'}
                if not required.issubset(reader.fieldnames or []):
                    raise ValueError(f'{source}: missing envelope columns')
                for row in reader:
                    name = row['dataset']
                    if name not in ALLOWED:
                        raise ValueError(f'Unknown dataset: {name}')
                    payload = json.loads(row['row_data'])
                    if not isinstance(payload, dict):
                        raise ValueError(f'{name}: row_data must be a JSON object')
                    info = metadata.setdefault(name, {'sources': set(), 'extracted_at': set(), 'databases': set(), 'timezones': set()})
                    for key, value in [('sources', str(source)), ('extracted_at', row['extracted_at']), ('databases', row['source_database']), ('timezones', row['reporting_timezone'])]:
                        info[key].add(value)
                    if row['record_type'] == 'manifest':
                        manifests.add(name)
                        continue
                    if row['record_type'] != 'data':
                        raise ValueError(f'{name}: invalid record_type')
                    fields = sorted(payload)
                    if name not in writers:
                        handles[name] = (output / f'{name}.csv').open('x', encoding='utf-8', newline='')
                        columns[name] = fields
                        writers[name] = csv.DictWriter(handles[name], fieldnames=fields)
                        writers[name].writeheader()
                    if fields != columns[name]:
                        raise ValueError(f'{name}: inconsistent payload columns')
                    writers[name].writerow({k: cell(v) for k, v in payload.items()})
                    counts[name] += 1
        if set(metadata) != manifests:
            raise ValueError('Data without its dataset manifest')
        report = {name: {**{k: sorted(v) for k, v in info.items()}, 'rows': counts[name], 'empty': counts[name] == 0} for name, info in sorted(metadata.items())}
        (output / 'unpack_manifest.json').write_text(json.dumps(report, indent=2) + '\n')
        (output / 'SUCCESS').write_text('Envelope unpacking completed. This does not certify dashboard metrics.\n')
        return report
    finally:
        for handle in handles.values():
            handle.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('sources', nargs='+', type=Path)
    args = parser.parse_args()
    result = unpack(args.sources, args.output)
    print(json.dumps({name: info['rows'] for name, info in result.items()}, indent=2))
