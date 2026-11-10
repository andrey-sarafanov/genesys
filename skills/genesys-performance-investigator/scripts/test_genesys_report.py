#!/usr/bin/env python3
"""Behavioral checks and synthetic demo generator; never accesses a tenant."""
import argparse
import json
import tempfile
import unittest
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from genesys_report import build_model, dt, iso, measures, merge_stats, plan, render


def metrics(offered=100, answered=90, handle_count=80, asa=20, aht=300, sl_num=75):
    return {'nOffered': {'count': offered}, 'tAnswered': {'count': answered, 'sum': answered * asa * 1000},
            'tHandle': {'count': handle_count, 'sum': handle_count * aht * 1000},
            'tAbandon': {'count': offered - answered, 'sum': (offered - answered) * 40000},
            'oServiceLevel': {'numerator': sl_num, 'denominator': offered}}


def bucket(iv, stats):
    return {'interval': iv, 'metrics': [{'metric': k, 'stats': v} for k, v in stats.items()]}


def fixture():
    iv = '2026-10-12T00:00:00Z/2026-10-13T00:00:00Z'
    manifest = {'title': 'Test', 'timezone': 'UTC', 'timezone_source': 'Synthetic test setting',
                'interval': iv, 'as_of': '2026-10-13T00:00:00Z',
                'entities': [{'kind': 'queue', 'id': 'q1', 'name': 'Queue 1'}],
                'datasets': [{'id': 'daily', 'kind': 'queue', 'granularity': 'P1D', 'file': 'raw.json', 'coverage': 'complete'}]}
    raw = {'results': [{'group': {'queueId': 'q1', 'mediaType': 'voice'}, 'data': [bucket(iv, metrics())]}]}
    return manifest, raw


class ReportingTests(unittest.TestCase):
    def model(self, manifest, raw):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'raw.json').write_text(json.dumps(raw))
            return build_model(manifest, base)

    def test_weighted_not_average_of_averages(self):
        a = {'stats': metrics(100, 90, 80, 20, 300, 75)}
        b = {'stats': metrics(10, 5, 4, 100, 900, 2)}
        v = measures(merge_stats([a, b]), 'queue', 'voice')
        self.assertAlmostEqual(v['ASA seconds'], 2300 / 95)
        self.assertAlmostEqual(v['AHT seconds'], 27600 / 84)
        self.assertAlmostEqual(v['Service level %'], 70)

    def test_zero_and_missing(self):
        v = measures({'nOffered': {'count': 0}, 'tAnswered': {'count': 0, 'sum': 0}}, 'queue', 'voice')
        self.assertEqual(v['Offered'], 0)
        self.assertIsNone(v['ASA seconds'])
        self.assertIsNone(v['AHT seconds'])
        pooled = merge_stats([{'stats': metrics()}, {'stats': {'nOffered': {'count': 50}}}])
        self.assertIsNone(measures(pooled, 'queue', 'voice')['AHT seconds'])

    def test_ratio_only_not_pooled(self):
        a = {'stats': {'oServiceLevel': {'ratio': .9}}}
        self.assertEqual(measures(merge_stats([a]), 'queue', 'voice')['Service level %'], 90)
        self.assertIsNone(measures(merge_stats([a, a]), 'queue', 'voice')['Service level %'])

    def test_callback_and_message(self):
        for media in ('callback', 'message'):
            self.assertIsNone(measures(metrics(), 'queue', media)['Abandon / offered %'])
        self.assertIsNone(measures(metrics(), 'queue', 'callback')['Answered'])

    def test_last_monday(self):
        p = plan('Europe/Kyiv', ['q'], as_of='2026-10-15T14:00:00+03:00')
        self.assertTrue(p['start_local'].startswith('2026-10-12T00:00:00+03:00'))
        p = plan('Europe/Kyiv', ['q'], as_of='2026-10-12T14:00:00+03:00')
        self.assertTrue(p['start_local'].startswith('2026-10-05'))

    def test_dst_fall_and_spring(self):
        for start, end, hours in [('2026-10-25', '2026-10-26T00:00:00+02:00', 25),
                                  ('2026-03-29', '2026-03-30T00:00:00+03:00', 23)]:
            p = plan('Europe/Kyiv', ['q'], start=start, as_of=end)
            a, b = map(dt, p['interval'].split('/'))
            self.assertEqual((b-a).total_seconds()/3600, hours)
            self.assertEqual(p['requests'][0]['request']['body']['timeZone'], 'Europe/Kyiv')

    def test_flow_only_and_selection_required(self):
        p = plan('UTC', flow_ids=['f1'], as_of='2026-10-15T00:00:00Z')
        self.assertEqual({r['kind'] for r in p['requests']}, {'flow'})
        with self.assertRaises(ValueError):
            plan('UTC')

    def test_requests_against_official_api_snapshot(self):
        snapshot = json.loads((Path(__file__).parent.parent / 'references/api-contract.json').read_text())
        p = plan('UTC', ['q1','q2','q3'], ['f1'], as_of='2026-10-15T12:00:00Z', flow_outcomes=True, flow_versions=True)
        self.assertEqual(len(p['requests']), 8)
        for item in p['requests']:
            name = 'FlowAggregationQuery' if item['kind']=='flow' else 'ConversationAggregationQuery'
            schema = snapshot['queries'][name]
            request = item['request']
            self.assertEqual(request['path'], schema['path'])
            self.assertTrue(set(request['body']['metrics']) <= set(schema['metrics']))
            self.assertTrue(set(request['body']['groupBy']) <= set(schema['groupBy']))

    def test_demo_build_and_daily_intraday_reconciliation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = demo(Path(temp))
            self.assertTrue(path.exists())
            m = json.loads((Path(temp)/'manifest.json').read_text())
            model = build_model(m, Path(temp))
            daily = next(r for r in model['summaries'] if r['dataset']=='queue-P1D' and r['entity_id']=='demo-q1')
            intraday = next(r for r in model['summaries'] if r['dataset']=='queue-PT30M' and r['entity_id']=='demo-q1')
            self.assertEqual(daily['values'], intraday['values'])

    def test_error_and_empty_are_not_zero(self):
        m, r = fixture()
        result = self.model(m, {'status': 403, 'message': 'Forbidden'})
        self.assertFalse(result['rows'])
        self.assertEqual(result['sources'][0]['coverage'], 'unavailable')
        result = self.model(m, {'results': []})
        self.assertFalse(result['rows'])
        self.assertTrue(any('no returned rows' in s for s in result['issues']))

    def test_duplicate_or_unselected_rejected(self):
        m, r = fixture()
        r['results'][0]['data'] *= 2
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            self.model(m, r)
        m, r = fixture()
        r['results'][0]['group']['queueId'] = 'q-other'
        with self.assertRaisesRegex(ValueError, 'unselected'):
            self.model(m, r)

    def test_daily_timezone_alignment_rejected(self):
        m, r = fixture()
        m['timezone'] = 'Europe/Kyiv'
        with self.assertRaisesRegex(ValueError, 'aligned'):
            self.model(m, r)

    def test_partial_and_envelope(self):
        m, r = fixture()
        m['interval'] = r['results'][0]['data'][0]['interval'] = '2026-10-12T00:00:00Z/2026-10-12T12:00:00Z'
        result = self.model(m, {'status': 200, 'data': r})
        self.assertTrue(result['rows'][0]['partial'])
        self.assertEqual(result['summaries'][0]['values']['Offered'], 100)

    def test_injection_escaped_and_no_remote_dependencies(self):
        m, r = fixture()
        m['title'] = m['entities'][0]['name'] = '</script><script>alert(99)</script>'
        page = render(self.model(m, r))
        self.assertNotIn('</script><script>alert(99)', page)
        self.assertNotIn('<script src=', page)
        self.assertNotIn('@import', page)
        self.assertIn('\\u003c/script', page)

    def test_flow_dimensions_and_custom_measures(self):
        m, r = fixture()
        m['entities'] = [{'kind': 'flow', 'id': 'f1', 'name': 'IVR'}]
        m['datasets'][0]['kind'] = 'flow'
        r['results'][0]['group'] = {'flowId': 'f1', 'mediaType': 'voice', 'flowOutcomeValue': 'SUCCESS'}
        r['results'][0]['data'][0]['metrics'] = [{'metric': 'nFlowOutcome', 'stats': {'count': 5}}]
        result = self.model(m, r)
        self.assertEqual(result['rows'][0]['dimensions']['flowOutcomeValue'], 'SUCCESS')
        self.assertEqual(result['rows'][0]['values']['nFlowOutcome count'], 5)
        self.assertIsNone(result['rows'][0]['values']['Flow executions'])


def demo(directory):
    directory.mkdir(parents=True, exist_ok=True)
    tz = ZoneInfo('Europe/Kyiv')
    begin = datetime(2026, 10, 12, tzinfo=tz)
    end = datetime(2026, 10, 15, 14, tzinfo=tz)
    p = plan('Europe/Kyiv', ['demo-q1','demo-q2','demo-q3'], ['demo-f1'], as_of=end.isoformat())
    entities = [{'kind':'queue','id':'demo-q'+str(i+1),'name':n} for i,n in enumerate(['Customer care','Billing','Technical support'])]
    entities += [{'kind':'flow','id':'demo-f1','name':'Main IVR'}]
    datasets = []
    for request in p['requests']:
        kind, gran = request['kind'], request['granularity']
        results = []
        for n, entity in enumerate(e for e in entities if e['kind'] == kind):
            buckets = []
            cursor = begin
            while cursor < end:
                stop = min(cursor + timedelta(minutes=30), end)
                day = (cursor.date() - begin.date()).days
                peak = 9 <= cursor.hour < 17
                offered = (8 + n * 3 + day * 2) if peak else 1
                answered = max(0, offered - (2 if peak and day == 1 else 1))
                stat = metrics(offered, answered, answered, 30 + day*10 + n*5, 230+n*45, max(0, answered-1))
                stat.update({'tAcw':{'count':answered,'sum':answered*(35+day*3)*1000},
                             'nTransferred':{'count':int(peak)},'tShortAbandon':{'count':0}})
                if kind == 'flow':
                    stat = {'nFlow':{'count':offered*3},'tFlow':{'count':offered*3,'sum':offered*3*(32+day*3)*1000}}
                buckets.append((cursor, stop, stat))
                cursor = stop
            if gran == 'P1D':
                grouped = defaultdict(list)
                for a,b,s in buckets:
                    grouped[a.date()].append((a,b,s))
                buckets = [(xs[0][0],xs[-1][1],merge_stats([{'stats':x[2]} for x in xs])) for xs in grouped.values()]
            results.append({'group':{kind+'Id':entity['id'],'mediaType':'voice'},
                            'data':[bucket(iso(a)+'/'+iso(b),s) for a,b,s in buckets]})
        (directory/request['response_file']).write_text(json.dumps({'results':results}))
        datasets.append({'id':kind+'-'+gran,'kind':kind,'granularity':gran,'slice':'base',
                         'coverage':'complete','file':request['response_file'], 'request':request['request'],
                         'note':'Synthetic fixture; complete generated coverage, with a partial final day.'})
    manifest = {'title':'Queue and IVR performance investigation','demo':True,'timezone':p['timezone'],
                'timezone_source':'Synthetic test setting; not discovered from any tenant',
                'interval':p['interval'],'as_of':p['as_of'],'entities':entities,'datasets':datasets,
                'limitations':['Synthetic demonstration only. No live Genesys access or customer data.',
                               '15 October ends at 14:00 local time; no full-day comparison.',
                               'No historical staffing, business targets or matched-week baseline collected.'],
                'findings':[{'observation':'In this synthetic fixture, Tuesday has longer answer waits than Monday.',
                    'hypothesis':'Arrival pressure could contribute; this demonstration does not establish a cause.',
                    'confidence':'Low: synthetic aggregates only',
                    'alternatives':['Different arrival pattern','Lower effective staffing','Longer interactions'],
                    'test':'On a live run, compare matched PT30M arrivals, historical staffing and handle workload.',
                    'owner':'Operations / WFM analyst',
                    'evidence':['queue-P1D.json; demo-q1; 2026-10-12 and 2026-10-13; tAnswered sum/count']} ]}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (directory/'plan.json').write_text(json.dumps(p,indent=2))
    model=build_model(manifest,directory)
    (directory/'report.html').write_text(render(model))
    return directory/'report.html'


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--demo-dir',type=Path)
    args,extra=parser.parse_known_args()
    if args.demo_dir:
        print(demo(args.demo_dir).resolve())
    else:
        unittest.main(argv=['test_genesys_report.py']+extra)
