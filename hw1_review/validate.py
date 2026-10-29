"""Validate HW1 record structure and required case coverage, without judging answers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {'role','user_id','store_id','request','tool_calls','response','expected',
            'requirement','met_requirement','problem_source'}


def validate_record(record: dict) -> list[str]:
    errors = [f'missing field {key}' for key in sorted(REQUIRED - record.keys())]
    if errors:
        return errors
    if record['role'] not in ('shopper','merchant','support'):
        errors.append('invalid role')
    if type(record['user_id']) is not int:
        errors.append('user_id must be an integer')
    if record['role'] == 'merchant' and type(record['store_id']) is not int:
        errors.append('merchant requires store_id')
    if record['role'] != 'merchant' and record['store_id'] is not None:
        errors.append('non-merchant store_id must be null')
    for key in ('request','response','expected'):
        if not isinstance(record[key],str) or not record[key].strip():
            errors.append(f'{key} must be nonempty text')
    if type(record['met_requirement']) is not bool:
        errors.append('met_requirement must be a finalized boolean')
    if record['problem_source'] not in ('prompt','tool','specification',None):
        errors.append('invalid problem_source')
    if record['met_requirement'] is False and record['problem_source'] is None:
        errors.append('failed record requires problem_source')
    if record['met_requirement'] is True and record['problem_source'] is not None:
        errors.append('passing record requires null problem_source')
    if record['requirement'] is not None and not isinstance(record['requirement'],str):
        errors.append('requirement must be text or null')
    if not isinstance(record['tool_calls'],list):
        errors.append('tool_calls must be a list')
    else:
        for i,call in enumerate(record['tool_calls'],1):
            if not isinstance(call,dict) or not {'name','arguments','result'} <= call.keys():
                errors.append(f'tool call {i} must include name, arguments and actual result')
    return errors


def validate_file(path: Path) -> tuple[list[dict],list[str]]:
    rows,errors=[],[]
    for line_number,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        try:
            row=json.loads(line)
        except json.JSONDecodeError:
            errors.append(f'line {line_number}: invalid JSON');continue
        if not isinstance(row,dict):
            errors.append(f'line {line_number}: expected object');continue
        rows.append(row)
        errors.extend(f'line {line_number}: {error}' for error in validate_record(row))
    if len(rows)<10:
        errors.append('at least 10 conversation records required')
    if {r.get('role') for r in rows} != {'shopper','merchant','support'}:
        errors.append('all three roles must be represented')
    for order_id in (4127,3980,4455):
        if not any(r.get('role')=='shopper' and r.get('user_id')==1 and str(order_id) in r.get('request','') for r in rows):
            errors.append(f'missing shopper1 case for order {order_id}')
    if not any(r.get('role')=='merchant' and r.get('user_id')==9002 and r.get('store_id')==2 and '4127' in r.get('request','') for r in rows):
        errors.append('missing merchant9002/store2 case for order4127')
    if not any(r.get('role')=='shopper' and r.get('user_id')==1 and 'new@example.com' in r.get('request','') for r in rows):
        errors.append('missing shopper1 email-change case')
    return rows,errors


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]/'hw1-session.jsonl')
    args=parser.parse_args();rows,errors=validate_file(args.path)
    if errors:
        for error in errors:print(error)
        raise SystemExit(1)
    print(f'Validated {len(rows)} assessed records; all three roles and required order/email identities present.')
    print('Scope refusal, store override, tool evidence and student judgments also require manual review.')


if __name__=='__main__':
    main()
