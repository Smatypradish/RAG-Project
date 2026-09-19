import unittest
from datetime import date, timedelta
from types import SimpleNamespace

from app.services.verification_engine import (
    calculate_reliability_score,
    classify_evidence,
)


def make_doc(**overrides):
    defaults = dict(
        id=1,
        original_name="Regulations",
        status="active",
        authority_level=5,
        effective_date=date.today() - timedelta(days=30),
        expiry_date=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_evidence(score, status="active"):
    return SimpleNamespace(relevance_score=score, status=status)


class ReliabilityScoreTests(unittest.TestCase):
    def test_out_of_domain_chunks_are_heavily_penalized(self):
        score = calculate_reliability_score({"distance": 1.5}, make_doc())
        self.assertLessEqual(score, 0.2)

    def test_active_current_document_scores_high(self):
        score = calculate_reliability_score({"distance": 0.3}, make_doc())
        self.assertGreater(score, 0.6)

    def test_expired_document_scores_lower_than_current(self):
        expired = make_doc(expiry_date=date.today() - timedelta(days=1))
        current = make_doc()
        s_expired = calculate_reliability_score({"distance": 0.3}, expired)
        s_current = calculate_reliability_score({"distance": 0.3}, current)
        self.assertLess(s_expired, s_current)

    def test_future_effective_date_is_penalized(self):
        future = make_doc(effective_date=date.today() + timedelta(days=90))
        s_future = calculate_reliability_score({"distance": 0.3}, future)
        s_current = calculate_reliability_score({"distance": 0.3}, make_doc())
        self.assertLess(s_future, s_current)

    def test_superseded_document_scores_below_active(self):
        superseded = make_doc(status="superseded")
        s_sup = calculate_reliability_score({"distance": 0.3}, superseded)
        s_act = calculate_reliability_score({"distance": 0.3}, make_doc())
        self.assertLess(s_sup, s_act)


class ClassificationTests(unittest.TestCase):
    def test_no_evidence_is_not_available(self):
        self.assertEqual(classify_evidence([], []), "not_available")

    def test_low_score_is_not_available(self):
        self.assertEqual(classify_evidence([make_evidence(0.1)], []), "not_available")

    def test_only_inactive_evidence_is_outdated(self):
        ev = [make_evidence(0.6, status="superseded")]
        self.assertEqual(classify_evidence(ev, []), "outdated")

    def test_strong_active_evidence_is_verified(self):
        ev = [make_evidence(0.6, status="active")]
        self.assertEqual(classify_evidence(ev, []), "verified")

    def test_conflicts_override_verified(self):
        ev = [make_evidence(0.6, status="active")]
        self.assertEqual(classify_evidence(ev, [object()]), "conflicting")


if __name__ == "__main__":
    unittest.main()
