"""Run the Cartwheel CLI and capture real completed turns for the HW1 viewer."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from agents import Runner, SQLiteSession
from agent import cli
from agent.agent import prompt_version

RECORDS = Path(__file__).resolve().parents[1] / 'hw1-session.jsonl'


def tool_calls(items) -> list[dict]:
    outputs = {item.call_id: item.output for item in items
               if item.type == 'tool_call_output_item' and item.call_id is not None}
    calls = []
    for item in items:
        if item.type != 'tool_call_item':
            continue
        raw = item.raw_item
        arguments = raw.get('arguments') if isinstance(raw, dict) else getattr(raw, 'arguments', None)
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                pass
        call = {'name': item.tool_name, 'arguments': arguments}
        if item.call_id in outputs:
            output = outputs[item.call_id]
            if isinstance(output, str):
                try:
                    output = json.loads(output)
                except json.JSONDecodeError:
                    pass
            call['result'] = output
        calls.append(call)
    return calls


def save_run(record: dict, path: Path = RECORDS) -> None:
    """Append a unique run or update its turns, preserving student review fields."""
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, 'r+', encoding='utf-8') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        lines = stream.readlines()
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            existing = json.loads(line)
            if existing.get('run_id') == record['run_id']:
                merged = dict(existing)
                for key in ('request', 'response', 'turns', 'tool_calls'):
                    merged[key] = record[key]
                lines[index] = json.dumps(merged, ensure_ascii=False) + '\n'
                break
        else:
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append(json.dumps(record, ensure_ascii=False) + '\n')
        stream.seek(0)
        stream.writelines(lines)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())


class RecordingRunner:
    def __init__(self, scenario: str, model: str, run_id: str, expected: str | None):
        self.turns = []
        self.scenario, self.model, self.run_id = scenario, model, run_id
        self.expected = expected
        self.version = prompt_version()

    async def run(self, agent, request, **kwargs):
        result = await Runner.run(agent, request, **kwargs)
        self.turns.append({'request': request, 'tool_calls': tool_calls(result.new_items),
                           'response': result.final_output})
        ctx = kwargs['context']
        record = {
            'scenario_id': self.scenario, 'run_id': self.run_id,
            'model': self.model, 'prompt_version': self.version,
            'role': ctx.role, 'user_id': ctx.user_id, 'store_id': ctx.store_id,
            'request': self.turns[0]['request'],
            'response': self.turns[-1]['response'],
            'tool_calls': [call for turn in self.turns for call in turn['tool_calls']],
            'turns': list(self.turns), 'expected': self.expected,
            'requirement': None, 'met_requirement': None, 'problem_source': None,
            'assessment_status': 'pending', 'observation': '',
        }
        save_run(record)
        print(f'\n[recorded] {self.run_id} · {len(self.turns)} turn(s) saved to hw1-session.jsonl', flush=True)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario-id', required=True, help='For example S06')
    parser.add_argument('--role', choices=['shopper', 'merchant', 'support'], required=True)
    parser.add_argument('--user', type=int, required=True)
    parser.add_argument('--model', default='gpt-4o-mini')
    parser.add_argument('--expected', help='Your expected behavior, written before the request')
    args = parser.parse_args()
    cli.load_env()
    ctx = cli.resolve_auth(args.role, args.user)
    scenario = args.scenario_id.upper()
    run_id = f'{scenario}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:6]}'
    recorder = RecordingRunner(scenario, args.model, run_id, args.expected)
    # Use the supplied CLI and a unique SDK session; leave agent behavior unchanged.
    cli.Runner = recorder
    cli.SQLiteSession = lambda _name, db: SQLiteSession(run_id, db)
    print(f'Recording {scenario} with {args.model}. Each completed turn saves automatically.')
    print('Type quit to end this conversation. Relaunch for a new scenario.')
    asyncio.run(cli.chat(ctx, args.model, debug=True))


if __name__ == '__main__':
    main()
