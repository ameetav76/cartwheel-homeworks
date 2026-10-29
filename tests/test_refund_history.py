"""The additional HW1 read tool: authorization, real history and no mutations."""
import hashlib
from pathlib import Path

import pytest

from agent import db
from agent.agent import TOOLS_BY_ROLE
from agent.auth import AuthContext
from agent.tools import get_refund_history_logic


@pytest.fixture
def refund_history(world_copy):
    with db.connection() as conn:
        older = db.insert_refund(conn, order_id=4455, amount_cents=1000,
                                 reason='Older partial refund', status='auto_approved', created_at='2026-06-27')
        same_date = db.insert_refund(conn, order_id=4455, amount_cents=2000,
                                     reason='Pending review', status='queued_for_approval', created_at='2026-06-28')
        newest_id = db.insert_refund(conn, order_id=4455, amount_cents=3000,
                                     reason='Another review', status='queued_for_approval', created_at='2026-06-28')
    return world_copy, [newest_id, same_date, older]


@pytest.mark.parametrize('ctx', [AuthContext(1, 'shopper'), AuthContext(9001, 'merchant', 1), AuthContext(9501, 'support')])
def test_authorized_history_and_read_only_behavior(refund_history, ctx):
    path, ids = refund_history
    before = hashlib.sha256(Path(path).read_bytes()).digest()
    result = get_refund_history_logic(ctx, 4455)
    assert result['ok'] is True
    assert result['order_id'] == 4455
    assert result['count'] == 3
    assert [r['refund_id'] for r in result['refunds']] == ids
    assert [r['amount_usd'] for r in result['refunds']] == [30, 20, 10]
    assert [r['status'] for r in result['refunds']] == ['queued_for_approval', 'queued_for_approval', 'auto_approved']
    assert result['refunds'][0]['reason'] == 'Another review'
    assert result['refunds'][0]['created_at'] == '2026-06-28'
    assert hashlib.sha256(Path(path).read_bytes()).digest() == before


@pytest.mark.parametrize('ctx', [AuthContext(2, 'shopper'), AuthContext(9002, 'merchant', 2)])
def test_denial_before_history_lookup(refund_history, ctx, monkeypatch):
    def forbidden_query(*args):
        pytest.fail('Unauthorized request must not retrieve refund records')
    monkeypatch.setattr(db, 'list_refunds_for_order', forbidden_query)
    result = get_refund_history_logic(ctx, 4455)
    assert result['ok'] is False and result['error'] == 'permission_denied'
    assert 'refunds' not in result
    assert '240' not in result['reason']


def test_no_history_and_missing_order(world):
    assert get_refund_history_logic(AuthContext(1, 'shopper'), 4455) == {
        'ok': True, 'order_id': 4455, 'refunds': [], 'count': 0}
    missing = get_refund_history_logic(AuthContext(1, 'shopper'), 999999)
    assert missing['ok'] is False and missing['error'] == 'not_found'


@pytest.mark.parametrize('role', ['shopper', 'merchant', 'support'])
def test_history_registered_for_each_role(role):
    matches = [tool for tool in TOOLS_BY_ROLE[role] if tool.name == 'get_refund_history']
    assert len(matches) == 1
    assert 'order_id' in matches[0].params_json_schema['properties']
