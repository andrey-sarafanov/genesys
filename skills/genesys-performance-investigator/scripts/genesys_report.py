#!/usr/bin/env python3
"""Offline Genesys query planner and evidence-preserving report builder (stdlib)."""
import argparse
import hashlib
import html
import json
import math
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

QUEUE_METRICS = ['nOffered', 'tAnswered', 'tAbandon', 'tHandle', 'oServiceLevel',
                 'tWait', 'tTalkComplete', 'tHeldComplete', 'tAcw', 'tShortAbandon', 'nTransferred']
FLOW_METRICS = ['nFlow', 'tFlow', 'tFlowDisconnect', 'tFlowExit']
UTC = timezone.utc


def dt(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp must include an offset: ' + value)
    return result


def interval(value):
    start, end = map(dt, value.split('/'))
    if end <= start:
        raise ValueError('Interval end must be after start')
    return start, end


def iso(value):
    return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')


def plan(tz_name, queue_ids=(), flow_ids=(), start=None, as_of=None, media=(), flow_outcomes=False, flow_versions=False):
    tz = ZoneInfo(tz_name)
    end = dt(as_of) if as_of else datetime.now(UTC).replace(microsecond=0)
    local = end.astimezone(tz)
    day = datetime.fromisoformat(start).date() if start else local.date() - timedelta(days=local.weekday() or 7)
    begin = datetime.combine(day, time(), tz)
    if begin >= end:
        raise ValueError('Start must precede as-of')
    if not queue_ids and not flow_ids:
        raise ValueError('User-selected queue or flow IDs are required')
    iv = iso(begin) + '/' + iso(end)
    out = {'timezone': tz_name, 'interval': iv, 'start_local': begin.isoformat(),
           'end_local': local.isoformat(), 'as_of': iso(end), 'requests': []}
    for kind, ids, metrics, domain in [('queue', queue_ids, QUEUE_METRICS, 'conversations'),
                                      ('flow', flow_ids, FLOW_METRICS, 'flows')]:
        if not ids:
            continue
        if any(not x.strip() for x in ids) or len(set(ids)) != len(ids):
            raise ValueError('IDs must be nonempty and distinct')
        clauses = [{'type': 'or', 'predicates': [{'type': 'dimension', 'dimension': kind + 'Id',
                    'value': x} for x in ids]}]
        if media:
            clauses.append({'type': 'or', 'predicates': [{'type': 'dimension', 'dimension': 'mediaType',
                            'value': x} for x in media]})
        slices = [('base', [], metrics)]
        if kind == 'flow' and flow_outcomes:
            slices.append(('outcomes', ['flowOutcomeId', 'flowOutcomeValue'], ['nFlowOutcome', 'nFlowOutcomeFailed', 'tFlowOutcome']))
        if kind == 'flow' and flow_versions:
            slices.append(('versions', ['flowVersion'], metrics))
        for slice_name, extra_groups, slice_metrics in slices:
            for gran in ('P1D', 'PT30M'):
                out['requests'].append({'kind': kind, 'granularity': gran, 'slice': slice_name,
                    'response_file': kind + ('-' + slice_name if slice_name != 'base' else '') + '-' + gran + '.json',
                    'request': {'method': 'POST', 'path': '/api/v2/analytics/' + domain + '/aggregates/query',
                        'body': {'interval': iv, 'timeZone': tz_name, 'granularity': gran,
                                 'groupBy': [kind + 'Id', 'mediaType'] + extra_groups,
                                 'filter': {'type': 'and', 'clauses': clauses}, 'metrics': slice_metrics}}})
    return out


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def ratio(n, d, scale=1):
    return n / d * scale if number(n) and number(d) and d > 0 else None


def measures(stats, kind, media):
    def get(metric, stat):
        return stats.get(metric, {}).get(stat)
    def avg(metric):
        return ratio(get(metric, 'sum'), get(metric, 'count'), .001)
    if kind == 'flow':
        result = {'Flow executions': get('nFlow', 'count'), 'Average flow seconds': avg('tFlow')}
        for metric, values in stats.items():
            if metric not in ('nFlow', 'tFlow'):
                if 'count' in values:
                    result[metric + ' count'] = values['count']
                if 'sum' in values and metric.startswith('t'):
                    result[metric + ' average seconds'] = avg(metric)
        return result
    offered = get('nOffered', 'count')
    sl = stats.get('oServiceLevel', {})
    result = {'Offered': offered, 'Answered': get('tAnswered', 'count'),
              'Abandoned': get('tAbandon', 'count'), 'Handled': get('tHandle', 'count'),
              'Service level %': ratio(sl.get('numerator'), sl.get('denominator'), 100)
                if 'denominator' in sl else (sl.get('ratio') * 100 if number(sl.get('ratio')) else None),
              'ASA seconds': avg('tAnswered'), 'AHT seconds': avg('tHandle'),
              'Abandon / offered %': ratio(get('tAbandon', 'count'), offered, 100),
              'Wait seconds': avg('tWait'), 'Talk seconds': avg('tTalkComplete'),
              'Hold seconds': avg('tHeldComplete'), 'ACW seconds': avg('tAcw'),
              'Short abandons': get('tShortAbandon', 'count'), 'Transfers': get('nTransferred', 'count')}
    if media == 'callback':
        for key in ('Answered', 'Abandoned', 'Service level %', 'ASA seconds', 'Abandon / offered %'):
            result[key] = None
    if media not in ('voice', 'callback'):
        result['Abandon / offered %'] = None
    return result


def merge_stats(rows):
    """Only sum a statistic if it is present on every disjoint contributing row."""
    if len(rows) == 1:
        return rows[0]['stats']
    merged = {}
    for metric in set().union(*(r['stats'] for r in rows)):
        target = {}
        for stat in ('count', 'sum', 'numerator', 'denominator'):
            values = [r['stats'].get(metric, {}).get(stat) for r in rows]
            if all(number(v) for v in values):
                target[stat] = sum(values)
        if target:
            merged[metric] = target
    return merged


def unwrap(payload):
    if not isinstance(payload, dict):
        raise ValueError('Response must be a JSON object')
    status = payload.get('status')
    if isinstance(status, int) and not 200 <= status < 300:
        raise ValueError('Source returned status ' + str(status))
    if isinstance(status, str) and status.lower() not in ('ok', 'success', 'complete', 'completed'):
        raise ValueError('Source returned status ' + status)
    if payload.get('error') or payload.get('scope_available') is False:
        raise ValueError('Source returned an error or missing scope')
    result = payload.get('data') if isinstance(payload.get('data'), dict) else payload
    if not isinstance(result.get('results'), list):
        raise ValueError('Expected results array; not a successful empty dataset')
    return result


def build_model(manifest, base):
    for field in ('title', 'timezone', 'timezone_source', 'interval', 'as_of', 'entities', 'datasets'):
        if field not in manifest:
            raise ValueError('Missing manifest field: ' + field)
    tz = ZoneInfo(manifest['timezone'])
    start, end = interval(manifest['interval'])
    if dt(manifest['as_of']) < end:
        raise ValueError('As-of timestamp cannot precede the report interval end')
    if not isinstance(manifest['datasets'], list) or not manifest['datasets']:
        raise ValueError('At least one dataset record is required, including for unavailable data')
    if not manifest['timezone_source']:
        raise ValueError('Timezone provenance is required')
    entities = {(e['kind'], e['id']): e['name'] for e in manifest['entities']}
    if len(entities) != len(manifest['entities']) or not entities:
        raise ValueError('Entities must be nonempty and distinct by kind/ID')
    rows, summaries, sources, issues = [], [], [], list(manifest.get('limitations', []))
    dataset_ids = set()
    for index, dataset in enumerate(manifest['datasets']):
        did = dataset.get('id', str(index + 1))
        if did in dataset_ids:
            raise ValueError('Duplicate dataset ID: ' + did)
        dataset_ids.add(did)
        kind, gran = dataset['kind'], dataset['granularity']
        if kind not in ('queue', 'flow') or gran not in ('P1D', 'PT30M', 'PT1H'):
            raise ValueError('Unsupported kind/granularity')
        ds_start, ds_end = interval(dataset.get('interval', manifest['interval']))
        if ds_start < start or ds_end > end:
            raise ValueError('Dataset interval outside manifest interval; use a separate comparison report')
        coverage = dataset.get('coverage', 'unknown')
        if coverage not in ('complete', 'provisional', 'partial', 'unknown', 'unavailable'):
            raise ValueError('Invalid coverage label')
        source = {'id': did, 'file': dataset['file'], 'kind': kind, 'granularity': gran,
                  'slice': dataset.get('slice', 'base'), 'coverage': coverage,
                  'interval': dataset.get('interval', manifest['interval']),
                  'request': dataset.get('request', {}), 'note': dataset.get('note', '')}
        sources.append(source)
        if coverage != 'complete':
            issues.append(f'{did}: source coverage is {coverage}. {source["note"]}')
        try:
            path = (base / dataset['file']).resolve()
            if not path.is_relative_to(base.resolve()):
                raise ValueError('Source file must stay within report directory')
            raw = path.read_bytes()
            source['sha256'] = hashlib.sha256(raw).hexdigest()
            payload = unwrap(json.loads(raw))
        except (ValueError, OSError) as exc:
            source['coverage'] = 'unavailable'
            issues.append(f'{did}: {exc}')
            continue
        local_rows, seen = [], defaultdict(list)
        for result in payload['results']:
            group = result['group']
            entity_id = group[kind + 'Id']
            if (kind, entity_id) not in entities:
                raise ValueError(f'{did}: unselected entity {entity_id}')
            media = group.get('mediaType', group.get('media_type', 'unspecified'))
            dims = {k: v for k, v in group.items() if k not in (kind + 'Id', 'mediaType', 'media_type')}
            dimension_key = json.dumps(dims, sort_keys=True)
            for bucket in result['data']:
                a, b = interval(bucket['interval'])
                if a < ds_start or a >= ds_end or b > ds_end:
                    raise ValueError(f'{did}: bucket outside requested interval; preserve and investigate')
                key = (entity_id, media, dimension_key)
                if any(a < y and b > x for x, y in seen[key]):
                    raise ValueError(f'{did}: duplicate or overlapping buckets')
                seen[key].append((a, b))
                stat_map = {}
                for metric in bucket.get('metrics') or []:
                    name = metric['metric']
                    # Qualified metrics require a dedicated semantic adapter, not silent addition.
                    if name in stat_map or metric.get('qualifier'):
                        raise ValueError(f'{did}: duplicate/qualified metric {name}; split the slice explicitly')
                    clean = {k: v for k, v in (metric.get('stats') or {}).items()
                             if k in ('count', 'sum', 'numerator', 'denominator', 'ratio') and v is not None}
                    if not all(number(v) for v in clean.values()):
                        raise ValueError(f'{did}: invalid numeric statistic')
                    stat_map[name] = clean
                la, lb = a.astimezone(tz), b.astimezone(tz)
                next_midnight = datetime.combine(la.date() + timedelta(days=1), time(), tz)
                if gran == 'P1D' and (la.time() != time() or b > next_midnight):
                    raise ValueError(f'{did}: daily bucket is not aligned to reporting calendar')
                partial = b < next_midnight if gran == 'P1D' else (b - a).total_seconds() < (1800 if gran == 'PT30M' else 3600)
                row = {'dataset': did, 'kind': kind, 'entity_id': entity_id, 'name': entities[(kind, entity_id)],
                       'media': media, 'dimensions': dims, 'dimension_key': dimension_key,
                       'start': iso(a), 'end': iso(b), 'local': la.isoformat(), 'day': la.date().isoformat(),
                       'partial': partial, 'stats': stat_map, 'source': dataset['file'],
                       'values': measures(stat_map, kind, media)}
                local_rows.append(row)
        for key, spans in seen.items():
            ordered = sorted(spans)
            gap = ordered[0][0] > ds_start or ordered[-1][1] < ds_end or any(x[1] < y[0] for x, y in zip(ordered, ordered[1:]))
            if gap:
                issues.append(f'{did}: gaps for {entities[(kind,key[0])]} / {key[1]}; omitted buckets are not assumed zero.')
        present = {r['entity_id'] for r in local_rows}
        for (ekind, eid), name in entities.items():
            if ekind == kind and eid not in present:
                issues.append(f'{did}: no returned rows for selected {name}; not evidence of zero activity.')
        groups = defaultdict(list)
        for row in local_rows:
            groups[(row['entity_id'], row['media'], row['dimension_key'])].append(row)
        for group_rows in groups.values():
            first = group_rows[0]
            combined = merge_stats(group_rows)
            summaries.append({**{k: first[k] for k in ('dataset','kind','entity_id','name','media','dimensions','dimension_key')},
                              'values': measures(combined, kind, first['media']), 'buckets': len(group_rows)})
        rows.extend(local_rows)
    findings = manifest.get('findings', [])
    for finding in findings:
        for key in ('observation', 'hypothesis', 'confidence', 'alternatives', 'test', 'owner', 'evidence'):
            if key not in finding:
                raise ValueError('Finding missing ' + key)
        if not finding['evidence']:
            raise ValueError('Every finding needs evidence references')
    return {'title': manifest['title'], 'timezone': manifest['timezone'], 'timezone_source': manifest['timezone_source'],
            'interval': manifest['interval'], 'as_of': manifest['as_of'], 'demo': manifest.get('demo', False),
            'local_window': start.astimezone(tz).isoformat() + ' / ' + end.astimezone(tz).isoformat(),
            'rows': sorted(rows, key=lambda r: (r['dataset'], r['start'], r['name'])),
            'summaries': summaries, 'sources': sources, 'issues': list(dict.fromkeys(issues)), 'findings': findings,
            'entities': manifest['entities']}


def render(model):
    template = Path(__file__).resolve().parent.parent / 'assets' / 'report.html'
    payload = json.dumps(model, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return template.read_text().replace('__TITLE__', html.escape(model['title'])).replace('__DATA__', payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('plan')
    p.add_argument('--timezone', required=True)
    p.add_argument('--queue-id', action='append', default=[])
    p.add_argument('--flow-id', action='append', default=[])
    p.add_argument('--media', action='append', default=[])
    p.add_argument('--flow-outcomes', action='store_true')
    p.add_argument('--flow-versions', action='store_true')
    p.add_argument('--start')
    p.add_argument('--as-of')
    p.add_argument('--output', type=Path, required=True)
    b = commands.add_parser('build')
    b.add_argument('--manifest', type=Path, required=True)
    b.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'plan':
        result = json.dumps(plan(args.timezone, args.queue_id, args.flow_id, args.start, args.as_of, args.media,
                                 args.flow_outcomes, args.flow_versions), indent=2)
    else:
        manifest = json.loads(args.manifest.read_text())
        result = render(build_model(manifest, args.manifest.parent))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding='utf-8')
    print(args.output.resolve())


if __name__ == '__main__':
    main()
