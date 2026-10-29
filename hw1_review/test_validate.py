from hw1_review.validate import validate_record


def record():
    return {'role':'shopper','user_id':1,'store_id':None,'request':'Question',
            'tool_calls':[],'response':'Answer','expected':'Expected answer',
            'requirement':None,'met_requirement':True,'problem_source':None}


def test_final_record_accepts_no_tool_response():
    assert validate_record(record())==[]


def test_pending_or_missing_expectations_are_not_submission_complete():
    r=record();r.update(expected=None,met_requirement=None)
    errors=validate_record(r)
    assert 'expected must be nonempty text' in errors
    assert 'met_requirement must be a finalized boolean' in errors


def test_missing_tool_result_and_unclassified_failure_are_rejected():
    r=record();r.update(met_requirement=False,tool_calls=[{'name':'get_order','arguments':{'order_id':1}}])
    errors=validate_record(r)
    assert 'failed record requires problem_source' in errors
    assert any('actual result' in error for error in errors)
