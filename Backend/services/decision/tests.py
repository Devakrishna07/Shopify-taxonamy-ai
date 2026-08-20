from django.test import SimpleTestCase

from .confidence import (
    DecisionStatus,
    evaluate_confidence,
)

from .alternatives import (
    build_alternatives,
)

from .review import (
    make_decision,
)

from .approval import (
    ReviewAction,
    approve_result,
)


class ConfidenceTests(SimpleTestCase):

    def test_high_confidence(self):

        result = evaluate_confidence(0.90)

        self.assertEqual(
            result,
            DecisionStatus.AUTO_APPROVED,
        )

    def test_exact_auto_threshold(self):

        result = evaluate_confidence(0.85)

        self.assertEqual(
            result,
            DecisionStatus.AUTO_APPROVED,
        )

    def test_medium_confidence(self):

        result = evaluate_confidence(0.70)

        self.assertEqual(
            result,
            DecisionStatus.NEEDS_REVIEW,
        )

    def test_exact_review_threshold(self):

        result = evaluate_confidence(0.60)

        self.assertEqual(
            result,
            DecisionStatus.NEEDS_REVIEW,
        )

    def test_low_confidence(self):

        result = evaluate_confidence(0.40)

        self.assertEqual(
            result,
            DecisionStatus.MANUAL_REVIEW,
        )

    def test_invalid_confidence(self):

        with self.assertRaises(ValueError):
            evaluate_confidence(1.5)


class AlternativeTests(SimpleTestCase):

    def test_primary_category_removed(self):

        candidates = [
            {
                "category_id": 1,
                "category_name": "Shirts",
                "confidence": 0.90,
            },
            {
                "category_id": 2,
                "category_name": "T-Shirts",
                "confidence": 0.80,
            },
        ]

        result = build_alternatives(
            candidates,
            primary_category_id=1,
        )

        ids = [
            item["category_id"]
            for item in result
        ]

        self.assertNotIn(1, ids)
        self.assertIn(2, ids)

    def test_alternatives_ranked(self):

        candidates = [
            {
                "category_id": 1,
                "category_name": "Shirts",
                "confidence": 0.60,
            },
            {
                "category_id": 2,
                "category_name": "T-Shirts",
                "confidence": 0.90,
            },
        ]

        result = build_alternatives(
            candidates
        )

        self.assertEqual(
            result[0]["category_id"],
            2,
        )

        self.assertEqual(
            result[0]["rank"],
            1,
        )


class DecisionTests(SimpleTestCase):

    def test_auto_approval(self):

        result = make_decision(
            primary_category={
                "category_id": 100,
            },
            confidence=0.90,
        )

        self.assertEqual(
            result.status,
            DecisionStatus.AUTO_APPROVED,
        )

        self.assertFalse(
            result.requires_review
        )

    def test_review(self):

        result = make_decision(
            primary_category={
                "category_id": 100,
            },
            confidence=0.70,
        )

        self.assertEqual(
            result.status,
            DecisionStatus.NEEDS_REVIEW,
        )

        self.assertTrue(
            result.requires_review
        )

    def test_manual_review(self):

        result = make_decision(
            primary_category={
                "category_id": 100,
            },
            confidence=0.40,
        )

        self.assertEqual(
            result.status,
            DecisionStatus.MANUAL_REVIEW,
        )

    def test_failed_inference(self):

        result = make_decision(
            primary_category=None,
            confidence=0,
            inference_failed=True,
        )

        self.assertEqual(
            result.status,
            DecisionStatus.FAILED,
        )


class ApprovalTests(SimpleTestCase):

    def test_approve(self):

        category = {
            "category_id": 100,
        }

        result = approve_result(
            action="APPROVE",
            ai_category=category,
        )

        self.assertEqual(
            result.action,
            ReviewAction.APPROVE,
        )

        self.assertEqual(
            result.final_category,
            category,
        )

    def test_reclassify(self):

        new_category = {
            "category_id": 200,
        }

        result = approve_result(
            action="RECLASSIFY",
            ai_category={
                "category_id": 100,
            },
            final_category=new_category,
        )

        self.assertEqual(
            result.final_category,
            new_category,
        )

    def test_reject(self):

        result = approve_result(
            action="REJECT",
            ai_category={
                "category_id": 100,
            },
        )

        self.assertEqual(
            result.action,
            ReviewAction.REJECT
        )

        self.assertIsNone(
            result.final_category
        )