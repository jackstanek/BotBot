import pytest

from botbot import report

def test_pruning_shared_probs_with_prob_attr():
    probs = {
        'PROB_DIR_NOT_WRITABLE': 'totally rad directory',
        'PROB_SAM_AND_BAM_EXIST': 'whoops my bade'
    }

    pruned = report.prune_shared_probs(probs, 'problems')
    assert 'PROB_SAM_AND_BAM_EXIST' in pruned
    assert 'PROB_DIR_NOT_WRITABLE' not in pruned

def test_pruning_shared_probs_with_non_prob_attr():
    stay = {
        'problems': {'PROB_SAM_AND_BAM_EXIST'}
    }

    leave = {
        'problems': {'PROB_FILE_NOT_GRPRD'}
    }

    probs = {
        'jack': [stay],
        'goof': [leave]
    }

    pruned = report.prune_shared_probs(probs, 'username')
    assert 'jack' in pruned
    assert pruned['goof'] is not None and len(pruned['goof']) == 0

def test_pruning_empty_with_prob_attr():
    probs = {'PROB_DIR_NOT_ACCESSIBLE': [],
             'PROB_SAM_AND_BAM_EXIST': [{}]}
    pruned = report.prune_empty_listings(probs, 'problems')
    assert 'PROB_DIR_NOT_ACCESSIBLE' not in pruned
    assert 'PROB_SAM_AND_BAM_EXIST' in pruned

def test_pruning_empty_with_non_prob_attr():
    probs = {'jack': [{'problems': {}}],
             'goof': [{'problems': {'PROB'}}]}
    pruned = report.prune_empty_listings(probs, 'username')
    assert 'jack' not in pruned
    assert 'goof' in pruned
