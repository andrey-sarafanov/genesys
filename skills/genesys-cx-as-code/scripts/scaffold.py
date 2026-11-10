#!/usr/bin/env python3
# Author: Andrey Sarafanov @ Miratech inc
"""Create a local Genesys project. No network calls, credentials, or applies."""
import argparse
import json
import re
from pathlib import Path

CHANNELS = ('ivr', 'voicebot', 'webmessaging', 'sms', 'whatsapp')
ASSETS = Path(__file__).resolve().parents[1] / 'assets'
TOKEN = re.compile(r'\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}')
BASE_CASES = ('success', 'agent_handoff', 'no_input', 'no_match', 'invalid_input', 'backend_failure')
EXTRA_CASES = {
    'ivr': ('dtmf_choices', 'closed_hours', 'repeat_menu'),
    'voicebot': ('speech_interruption', 'slot_correction', 'ambiguous_intent'),
    'webmessaging': ('domain_restriction', 'reload_resume', 'agent_reply'),
    'sms': ('delayed_reply', 'unicode_message', 'opt_out', 'duplicate_message'),
    'whatsapp': ('template_parameters', 'service_window_expired', 'media_fallback', 'agent_reply'),
}

def dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + '\n'

def build(name, channels, version, seeds=None, substitutions=None, bot_engines=None):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,62}', name):
        raise ValueError('name must start with a lowercase letter and contain lowercase letters, digits, or hyphens')
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('provider-version must be an exact x.y.z version')
    channels = list(dict.fromkeys(channels))
    if not channels or any(c not in CHANNELS for c in channels):
        raise ValueError('choose at least one supported channel')
    engines = {c: {'ivr': 'none', 'voicebot': 'native', 'webmessaging': 'digital',
                   'sms': 'native', 'whatsapp': 'digital'}[c] for c in channels}
    for channel, engine in (bot_engines or {}).items():
        if channel not in channels:
            raise ValueError(f'bot engine specified for unrequested channel {channel}')
        allowed = {'none'} if channel == 'ivr' else ({'native', 'external'} if channel == 'voicebot' else {'native', 'digital', 'external', 'none'})
        if engine not in allowed:
            raise ValueError(f'{channel} supports bot engines {sorted(allowed)}')
        engines[channel] = engine
    resources = {'genesyscloud_flow': {}}
    variables = {
        'name_prefix': {'type': 'string', 'default': name},
        'environment': {'type': 'string', 'default': 'dev'},
        'division_name': {'type': 'string', 'default': 'Home'},
        'queue_name': {'type': 'string', 'description': 'Existing target ACD queue name'},
    }
    config = {
        'terraform': {'required_version': '>= 1.5.0, < 2.0.0', 'required_providers': {
            'genesyscloud': {'source': 'MyPureCloud/genesyscloud', 'version': version}}},
        'provider': {'genesyscloud': {}}, 'variable': variables, 'resource': resources,
        'data': {'genesyscloud_routing_queue': {'handoff': {'name': '${var.queue_name}'}}},
        'output': {},
    }
    files, flows = {}, []

    def flow(label, filename, seed, root, serving, dependencies=(), bot_label=None):
        source = seeds / filename if seeds and (seeds / filename).is_file() else ASSETS / seed
        text = source.read_text(encoding='utf-8-sig')
        values = {
            'flow_name': '${var.name_prefix} ' + label.replace('_', ' ').title() + ' (${var.environment})',
            'division_name': '${var.division_name}',
            'default_language': 'en-us',
            'description': 'Generated starter; implement the requested journey before release.',
            'greeting': 'Welcome to the service desk.',
            'menu_disconnect_name': 'Finish example',
            'queue_name': '${data.genesyscloud_routing_queue.handoff.name}',
        }
        if bot_label:
            values['bot_flow_name'] = '${genesyscloud_flow.' + bot_label + '.name}'
        values.update(substitutions or {})
        keys = set(TOKEN.findall(text))
        unknown = keys - values.keys()
        if unknown:
            raise ValueError(f'{filename}: supply --substitution for {", ".join(sorted(unknown))}')
        mapped = {k: values[k] for k in sorted(keys)}
        resource = {'filepath': '${path.module}/flows/' + filename, 'substitutions': mapped}
        if dependencies:
            resource['depends_on'] = ['genesyscloud_flow.' + d for d in dependencies]
        resources['genesyscloud_flow'][label] = resource
        files['flows/' + filename] = text
        flows.append({'resource': label, 'path': 'flows/' + filename, 'root': root,
                      'channels': list(serving), 'substitutions': sorted(keys)})
        config['output'][label + '_id'] = {'value': '${genesyscloud_flow.' + label + '.id}'}

    if 'ivr' in channels:
        flow('ivr', 'ivr.yaml', 'ivr.yaml', 'inboundCall', ['ivr'])
    if 'voicebot' in channels:
        if engines['voicebot'] == 'native':
            flow('voice_bot', 'voice-bot.yaml', 'native-bot.yaml', 'botFlow', ['voicebot'])
            flow('voice_inbound', 'voice-inbound.yaml', 'voice-inbound.yaml', 'inboundCall',
                 ['voicebot'], ['voice_bot'], 'voice_bot')
        else:
            # Author the selected external connector in this entry flow; never substitute a native engine.
            flow('voice_inbound', 'voice-inbound.yaml', 'ivr.yaml', 'inboundCall', ['voicebot'])
    if any(c in channels for c in ('ivr', 'voicebot')):
        variables['dnis'] = {'type': 'list(string)', 'default': [], 'description': 'Authorized E.164 inbound numbers'}
        resources['genesyscloud_architect_ivr'] = {}
        for channel, label in [('ivr', 'ivr'), ('voicebot', 'voice_inbound')]:
            if channel in channels:
                # Separate lists avoid assigning the same number to two entry points.
                variable = 'dnis' if channel == 'ivr' else 'voicebot_dnis'
                if variable != 'dnis':
                    variables[variable] = {'type': 'list(string)', 'default': []}
                resources['genesyscloud_architect_ivr'][channel] = {
                    'name': '${var.name_prefix} ' + channel + ' (${var.environment})',
                    'dnis': '${var.' + variable + '}',
                    'open_hours_flow_id': '${genesyscloud_flow.' + label + '.id}',
                }
    for channel in [c for c in channels if c in ('webmessaging', 'sms', 'whatsapp')]:
        engine = engines[channel]
        bot_label = channel + '_bot'
        if engine in ('digital', 'native'):
            bot_seed, bot_root, message_seed = ('digital-bot.yaml', 'digitalBot', 'message-digital.yaml') if engine == 'digital' else ('native-bot.yaml', 'botFlow', 'message-native.yaml')
            flow(bot_label, channel + '-bot.yaml', bot_seed, bot_root, [channel])
            flow(channel + '_inbound', channel + '-inbound.yaml', message_seed,
                 'inboundShortMessage', [channel], [bot_label], bot_label)
        else:
            flow(channel + '_inbound', channel + '-inbound.yaml', 'message.yaml',
                 'inboundShortMessage', [channel])
    if 'sms' in channels:
        variables['sms_number'] = {'type': 'string', 'default': '', 'description': 'Already provisioned test sender/entry number'}
    if 'webmessaging' in channels:
        variables['allowed_domains'] = {'type': 'list(string)', 'default': []}
        variables['activate_messenger'] = {'type': 'bool', 'default': False}
        resources['genesyscloud_webdeployments_configuration'] = {'messenger': {
            'name': '${var.name_prefix} Messenger (${var.environment})',
            'default_language': 'en-us', 'languages': ['en-us'],
            'messenger': [{'enabled': True, 'launcher_button': [{'visibility': 'On'}],
                           'home_screen': [{'enabled': False}]}],
        }}
        resources['genesyscloud_webdeployments_deployment'] = {'messenger': {
            'name': '${var.name_prefix} Web (${var.environment})',
            'allowed_domains': '${var.allowed_domains}', 'allow_all_domains': False,
            'status': '${var.activate_messenger ? "Active" : "Inactive"}',
            'flow_id': '${genesyscloud_flow.webmessaging_inbound.id}',
            'configuration': [{'id': '${genesyscloud_webdeployments_configuration.messenger.id}',
                               'version': '${genesyscloud_webdeployments_configuration.messenger.version}'}],
        }}
        config['output']['messenger_snippet'] = {'value': '${genesyscloud_webdeployments_deployment.messenger.snippet}'}
        files['web/index.html'] = '<!doctype html>\n<html lang="en"><meta charset="utf-8"><title>Messenger test</title>\n<body><h1>Support conversation</h1><p>Insert the generated Messenger deployment snippet after authorized deployment.</p></body></html>\n'
    if 'whatsapp' in channels:
        variables['whatsapp_integration_name'] = {'type': 'string', 'description': 'Existing authorized WhatsApp integration'}
        config['data']['genesyscloud_conversations_messaging_integrations_whatsapp'] = {
            'existing': {'name': '${var.whatsapp_integration_name}'}}
        config['output']['whatsapp_integration_id'] = {
            'value': '${data.genesyscloud_conversations_messaging_integrations_whatsapp.existing.id}'}
    setup_details = {
        'ivr': 'Populate DNIS and add hours/queue routing requested by the journey.',
        'voicebot': 'Populate voicebot DNIS and complete returned intent/slot handling and queue fallback.',
        'webmessaging': 'Populate allowed domains; install generated snippet; activate only for the authorized release.',
        'sms': 'Provision/reference number and attach it to sms_inbound through a verified Message Routing operation.',
        'whatsapp': 'Reference/onboard the integration and attach its address to whatsapp_inbound through Message Routing.',
    }
    manifest = {'name': name, 'channels': channels, 'bot_engines': engines, 'provider_version': version,
                'implementation_complete': False, 'implementation_evidence': [], 'flows': flows,
                'channel_setup': {c: {'status': 'pending', 'evidence': [], 'required_work': setup_details[c]} for c in channels}}
    for channel, engine in engines.items():
        if engine == 'external':
            manifest['channel_setup'][channel]['required_work'] += ' Implement the selected external bot connector, its runtime/intent/slot contract, and fallback; the entry seed does not yet call it.'
    scenarios = [{'id': c + ':' + case, 'channel': c, 'case': case, 'outcome': 'not_run',
                  'environment': '', 'evidence': []} for c in channels for case in BASE_CASES + EXTRA_CASES[c]]
    files['main.tf.json'] = dump(config)
    files['journey.json'] = dump(manifest)
    files['tests/scenarios.json'] = dump(scenarios)
    env = {'environment': 'dev', 'queue_name': 'SET_EXISTING_QUEUE_NAME'}
    if 'whatsapp' in channels:
        env['whatsapp_integration_name'] = 'SET_EXISTING_WHATSAPP_INTEGRATION_NAME'
    files['envs/dev.tfvars.json.example'] = dump(env)
    files['.gitignore'] = '.terraform/\n*.tfstate\n*.tfstate.*\n*.tfplan\n*.tfvars\n*.tfvars.json\n.env*\ncrash.log\n'
    files['AGENTS.md'] = ('# Genesys application working agreements\n\n'
        'Use the genesys-cx-as-code skill. Complete every channel in journey.json. The generated seeds are examples, not the requested business application.\n'
        'Run local YAML and Terraform validation. Record live test evidence separately; never mark unperformed scenarios passed.\n'
        'Keep credentials outside source files. Apply/publish/send only within the user-authorized target and action scope.\n')
    files['BUILD.md'] = ('# Build and verify the conversation application\n\n'
        'Complete the requested journey, native/digital bot behavior, fallbacks, and channel setup in journey.json.\n'
        'Copy envs/dev.tfvars.json.example to a local ignored values file and fill the environment-specific values.\n'
        'Use separate roots/backends and credentials for other organizations. This example uses Terraform\'s default local state.\n\n'
        'Run `terraform init -backend=false`, `terraform fmt -check`, and `terraform validate` for local configuration checks.\n'
        'Run this skill\'s validate_project.py against this directory. Inspect Architect schemas/expressions separately.\n'
        'For an authorized connected release, verify org/region/backend, create/review a destination-specific plan, then apply. Flow apply publishes.\n'
        'Complete Message Routing for SMS/WhatsApp and snippet setup for Messenger. Record tests/scenarios.json evidence.\n'
        'Rollback requires restoring known-good code/flow versions and prior routing, followed by entry-point tests.\n')
    for license_file in ASSETS.glob('*LICENSE.txt'):
        files['licenses/' + license_file.name] = license_file.read_text(encoding='utf-8')
    return files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--channels', nargs='+', choices=CHANNELS, required=True)
    parser.add_argument('--provider-version', default='1.87.0')
    parser.add_argument('--seed-dir', type=Path)
    parser.add_argument('--substitution', action='append', default=[], metavar='KEY=VALUE')
    parser.add_argument('--bot-engine', action='append', default=[], metavar='CHANNEL=ENGINE',
                        help='Preserve native, digital, external, or none per selected channel')
    args = parser.parse_args()
    try:
        target = args.output.resolve()
        if target.exists() and (not target.is_dir() or any(target.iterdir())):
            raise ValueError('output must be a new or empty directory; no existing files are overwritten')
        extra = {}
        for item in args.substitution:
            key, sep, value = item.partition('=')
            if not sep or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key):
                raise ValueError('substitution must be KEY=VALUE with an identifier key')
            extra[key] = value
        engines = {}
        for item in args.bot_engine:
            channel, sep, engine = item.partition('=')
            if not sep:
                raise ValueError('bot-engine must be CHANNEL=ENGINE')
            engines[channel] = engine
        files = build(args.name, args.channels, args.provider_version, args.seed_dir, extra, engines)
        target.mkdir(parents=True, exist_ok=True)
        for relative, content in files.items():
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        print(dump({'project': str(target), 'channels': list(dict.fromkeys(args.channels)),
                    'files_created': len(files), 'implementation_complete': False}))
        return 0
    except (ValueError, OSError) as error:
        parser.exit(2, f'Error: {error}\n')

if __name__ == '__main__':
    raise SystemExit(main())
