#!/usr/bin/env python3
# Author: Andrey Sarafanov @ Miratech inc
"""Validate scaffold project structure; optional Terraform checks. Never applies."""
import argparse
import json
import re
import subprocess
from pathlib import Path

CHANNEL_ROOTS = {'ivr': {'inboundCall'}, 'voicebot': {'inboundCall'},
                 'webmessaging': {'inboundShortMessage'},
                 'sms': {'inboundShortMessage'}, 'whatsapp': {'inboundShortMessage'}}
TOKENS = re.compile(r'\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}')

def descendants(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from descendants(child)
    elif isinstance(value, list):
        for child in value:
            yield from descendants(child)

def within(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'path leaves project: {relative}')
    return path

def check_project(root, readiness=False):
    try:
        import yaml
        if not hasattr(yaml, 'SafeLoader'):
            raise ImportError('PyYAML is unavailable to this Python process')
    except ImportError as error:
        return [f'{error}; install PyYAML for this Python interpreter'], []

    class StrictLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            mapping = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                try:
                    if key in mapping:
                        raise ValueError(f'duplicate YAML key: {key}')
                    mapping[key] = self.construct_object(value_node, deep=deep)
                except TypeError as error:
                    raise ValueError('invalid mapping key; check substitution quoting') from error
            return mapping

    errors, notes = [], []
    try:
        manifest = json.loads((root / 'journey.json').read_text(encoding='utf-8-sig'))
        config = json.loads((root / 'main.tf.json').read_text(encoding='utf-8-sig'))
        scenarios = json.loads((root / 'tests/scenarios.json').read_text(encoding='utf-8-sig'))
        if not isinstance(manifest, dict) or not isinstance(config, dict) or not isinstance(scenarios, list):
            raise ValueError('manifest/config must be objects and scenarios an array')
        channels = manifest['channels']
        flows = manifest['flows']
        if not isinstance(channels, list) or not channels or len(set(channels)) != len(channels):
            raise ValueError('channels must be a nonempty unique list')
        if set(channels) - CHANNEL_ROOTS.keys():
            raise ValueError('manifest includes unsupported channels')
        engines = manifest.get('bot_engines', {})
        requirements = {c: set(CHANNEL_ROOTS[c]) for c in channels}
        for channel in channels:
            engine = engines.get(channel)
            allowed = {'none'} if channel == 'ivr' else ({'native', 'external'} if channel == 'voicebot' else {'native', 'digital', 'external', 'none'})
            if engine not in allowed:
                raise ValueError(f'{channel}: missing or unsupported bot engine')
            if engine in ('native', 'digital'):
                requirements[channel].add('botFlow' if engine == 'native' else 'digitalBot')
        if not isinstance(flows, list) or not flows:
            raise ValueError('manifest must include required flows')
        configured = config.get('resource', {}).get('genesyscloud_flow', {})
        pinned = config.get('terraform', {}).get('required_providers', {}).get('genesyscloud', {}).get('version')
        if pinned != manifest.get('provider_version'):
            errors.append('manifest provider version differs from Terraform pin')
        expected_labels = [f['resource'] for f in flows]
        if len(set(expected_labels)) != len(expected_labels) or set(expected_labels) != set(configured):
            errors.append('manifest flow resource coverage differs from Terraform configuration')
        coverage = {c: set() for c in channels}
        for flow in flows:
            label = flow['resource']
            path = within(root, flow['path'])
            if not path.is_file():
                errors.append(f'{label}: missing YAML file {flow["path"]}')
                continue
            text = path.read_text(encoding='utf-8-sig')
            required_tokens = set(TOKENS.findall(text))
            mapped = configured.get(label, {}).get('substitutions', {})
            if not isinstance(mapped, dict) or any(not isinstance(v, str) for v in mapped.values()):
                errors.append(f'{label}: substitutions must be a string map')
                continue
            if required_tokens - mapped.keys():
                errors.append(f'{label}: missing substitutions {sorted(required_tokens - mapped.keys())}')
            if required_tokens != set(flow.get('substitutions', [])):
                errors.append(f'{label}: manifest substitution list differs from YAML')
            expected_filepath = '${path.module}/' + flow['path']
            if configured.get(label, {}).get('filepath') != expected_filepath:
                errors.append(f'{label}: Terraform filepath differs from manifest')
            # Archy substitutes before parsing; deterministic safe identifiers permit unquoted template keys.
            def replacement(match):
                value = mapped.get(match.group(1), '')
                return value if re.fullmatch(r'[A-Za-z0-9_-]+', value) else 'seed_' + match.group(1)
            rendered = TOKENS.sub(replacement, text)
            for target in re.findall(r'genesyscloud_flow\.([A-Za-z0-9_]+)\.', json.dumps(configured.get(label, {}))):
                if target not in configured:
                    errors.append(f'{label}: referenced flow {target} is not configured')
            try:
                document = yaml.load(rendered, Loader=StrictLoader)
                if not isinstance(document, dict) or set(document) != {flow['root']}:
                    raise ValueError(f'expected exactly the {flow["root"]} root')
                body = document[flow['root']]
                if not isinstance(body, dict):
                    raise ValueError('flow body must be a mapping')
                for field in ('name', 'defaultLanguage', 'startUpRef'):
                    if not isinstance(body.get(field), str) or not body[field].strip():
                        raise ValueError(f'missing {field}')
                supported = body.get('supportedLanguages')
                if isinstance(supported, dict) and body['defaultLanguage'] not in supported:
                    raise ValueError('default language is absent from supported languages')
                nodes = list(descendants(body))
                ids = [node['refId'] for node in nodes if 'refId' in node]
                if any(not isinstance(i, str) for i in ids) or len(ids) != len(set(ids)):
                    raise ValueError('reference IDs must be unique strings')
                reference = re.search(r'\[([^\]]+)\]$', body['startUpRef'])
                if not reference or reference.group(1) not in ids:
                    raise ValueError('startup reference does not resolve to a refId')
                if not any(isinstance(node.get('actions'), list) and node['actions'] for node in nodes) and not body.get('menus'):
                    raise ValueError('flow contains no actions or menu')
                for channel in flow['channels']:
                    if channel not in coverage:
                        raise ValueError(f'flow refers to unrequested channel {channel}')
                    coverage[channel].add(flow['root'])
                notes.append(f'{label}: YAML shape and substitutions checked')
            except (yaml.YAMLError, ValueError, TypeError) as error:
                errors.append(f'{label}: {error}')
        for channel in channels:
            if not requirements[channel].issubset(coverage[channel]):
                errors.append(f'{channel}: missing required flow roots {sorted(requirements[channel] - coverage[channel])}')
            if channel not in manifest.get('channel_setup', {}):
                errors.append(f'{channel}: channel setup is absent')
            cases = {case.get('case') for case in scenarios if isinstance(case, dict) and case.get('channel') == channel}
            if not {'success', 'agent_handoff', 'no_input', 'no_match', 'invalid_input', 'backend_failure'}.issubset(cases):
                errors.append(f'{channel}: required acceptance scenarios are missing')
        ids = [case.get('id') for case in scenarios if isinstance(case, dict)]
        if len(ids) != len(scenarios) or any(not isinstance(i, str) for i in ids) or len(ids) != len(set(ids)):
            errors.append('scenario IDs must be unique strings')
        if any(case.get('channel') not in channels for case in scenarios if isinstance(case, dict)):
            errors.append('scenario belongs to an unrequested channel')
        if readiness:
            def evidence(records, description):
                if not isinstance(records, list) or not records:
                    errors.append(f'{description}: no evidence files')
                    return
                for relative in records:
                    path = within(root, relative)
                    if not path.is_file() or not path.stat().st_size:
                        errors.append(f'{description}: evidence missing or empty: {relative}')
            if manifest.get('implementation_complete') is not True:
                errors.append('requested business implementation remains incomplete')
            evidence(manifest.get('implementation_evidence'), 'implementation')
            for channel in channels:
                setup = manifest.get('channel_setup', {}).get(channel, {})
                if setup.get('status') != 'verified':
                    errors.append(f'{channel}: channel wiring not verified')
                evidence(setup.get('evidence'), channel + ' setup')
            for scenario in scenarios:
                if not isinstance(scenario, dict):
                    continue
                if scenario.get('outcome') != 'passed' or not scenario.get('environment'):
                    errors.append(f'{scenario.get("id")}: scenario not passed in a named environment')
                evidence(scenario.get('evidence'), str(scenario.get('id')))
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f'project inspection failed: {error}')
    return errors, notes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--terraform', help='Terraform executable; requires prior init -backend=false')
    parser.add_argument('--readiness', action='store_true', help='Check recorded implementation/setup/scenario evidence')
    args = parser.parse_args()
    root = args.project.resolve()
    errors, notes = check_project(root, args.readiness)
    if args.terraform:
        for command in ([args.terraform, 'fmt', '-check', '-recursive'], [args.terraform, 'validate', '-json']):
            try:
                result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=120)
                if result.returncode:
                    errors.append(f'Terraform {command[1]} failed: {(result.stdout + result.stderr).strip()}')
                else:
                    notes.append('Terraform ' + command[1] + ' passed')
            except (OSError, subprocess.TimeoutExpired) as error:
                errors.append(f'Terraform {command[1]} could not complete: {error}')
    print(json.dumps({'passed': not errors, 'scope': 'recorded-readiness' if args.readiness else 'local-structure',
                      'checks': notes, 'errors': errors, 'live_genesys_tested': False}, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
