from django.utils import timezone

from products.models import Product
from processing.models import ProcessingJob

from taxonamy.models import TaxonomyCategory

from services.ai import (
    AIInferenceService,
    ProductInput,
)

# ============================================================
# NEW DECISION & REVIEW SERVICE
# ============================================================
from services.decision import (
    DecisionStatus,
    make_decision,
)


class ProductPipeline:
    """
    Main orchestration layer for product processing.

    Responsibilities:
        1. Normalize product signals.
        2. Load Shopify taxonomy.
        3. Call the existing AI inference service.
        4. Pass AI classification to the existing
           Classification module.
        5. Pass AI attributes to the existing
           Attributes module.
        6. Run Decision & Review against the AI result.
        7. Persist taxonomy result.
        8. Persist Decision & Review state.
        9. Determine final processing status.

    Important architecture rule:
        The AI Inference module remains the actual
        intelligence layer.

        Decision & Review does NOT replace AI inference.
        It consumes the AI result and decides whether
        that result should be auto-approved, reviewed,
        manually reviewed, or marked failed.
    """

    def __init__(self, product):
        self.product = product

        # Existing AI service reference.
        self.ai_service = None

        # Decision result is stored here after inference.
        self.decision_result = None

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    def run(self):
        """
        Execute the complete product processing pipeline.

        Flow:

            Product
                ↓
            Normalize
                ↓
            Taxonomy
                ↓
            AI Inference
                ↓
            Classification
                ↓
            Attributes
                ↓
            Decision & Review
                ↓
            Taxonomy Result
                ↓
            Final Status
        """

        self._set_status("PROCESSING")

        try:

            # -------------------------------------------------
            # STEP 1
            # Normalize product
            # -------------------------------------------------

            product_input = self.build_product_input()

            # -------------------------------------------------
            # STEP 2
            # Load taxonomy
            # -------------------------------------------------

            categories = (
                TaxonomyCategory.objects.filter(
                    is_archived=False
                )
            )

            # -------------------------------------------------
            # EXISTING AI INFERENCE INTEGRATION
            # -------------------------------------------------
            #
            # This section is intentionally preserved.
            #
            # The Decision & Review module does NOT replace
            # the AIInferenceService.
            # -------------------------------------------------

            self.ai_service = AIInferenceService(
                categories
            )

            # -------------------------------------------------
            # STEP 3
            # AI inference
            # -------------------------------------------------

            ai_result = self.ai_service.infer(
                product_input
            )

            # -------------------------------------------------
            # STEP 4
            # Existing Classification module
            # -------------------------------------------------
            #
            # Classification executes BEFORE Decision & Review
            # so that the existing ClassificationResult can
            # already exist when DecisionReview is persisted.
            # -------------------------------------------------

            classification_result = (
                self.run_classification(
                    ai_result
                )
            )

            # -------------------------------------------------
            # STEP 5
            # Existing Attributes module
            # -------------------------------------------------

            attribute_result = (
                self.run_attributes(
                    classification_result,
                    ai_result,
                )
            )

            # -------------------------------------------------
            # STEP 6
            # Decision & Review
            # -------------------------------------------------

            decision_result = self.run_decision(
                ai_result
            )

            self.decision_result = decision_result

            # -------------------------------------------------
            # STEP 7
            # Persist taxonomy result
            # -------------------------------------------------

            self.persist_taxonomy_result(
                ai_result,
                decision_result,
            )

            # -------------------------------------------------
            # STEP 8
            # Final processing status
            # -------------------------------------------------

            self.update_final_status(
                ai_result,
                decision_result,
            )

            # -------------------------------------------------
            # FINAL RESPONSE
            # -------------------------------------------------

            return {
                "success": True,

                "product_id": self.product.id,

                "classification": (
                    classification_result
                ),

                "ai_inference": (
                    ai_result.to_dict()
                ),

                "attributes": (
                    attribute_result
                ),

                "decision": (
                    self._decision_to_dict(
                        decision_result
                    )
                ),

                "status": self.product.status,
            }

        except Exception as exc:

            # Existing failure-isolation behaviour is retained.
            self._set_status("FAILED")

            return {
                "success": False,

                "product_id": self.product.id,

                "error": str(exc),

                "status": "FAILED",
            }

    # =========================================================
    # PRODUCT INPUT
    # =========================================================

    def build_product_input(self):
        """
        Convert the existing Product model into the
        standard AI ProductInput schema.

        getattr() is intentionally used so this layer
        remains tolerant of optional product fields.
        """

        return ProductInput(
            product_id=self.product.id,

            title=(
                getattr(
                    self.product,
                    "title",
                    "",
                )
                or ""
            ),

            description=(
                getattr(
                    self.product,
                    "description",
                    "",
                )
                or ""
            ),

            product_type=(
                getattr(
                    self.product,
                    "product_type",
                    "",
                )
                or ""
            ),

            brand=(
                getattr(
                    self.product,
                    "brand",
                    "",
                )
                or ""
            ),

            image_url=self._get_image_url(),
        )

    # =========================================================
    # IMAGE
    # =========================================================

    def _get_image_url(self):
        """
        Return the product image URL when available.

        Supports both:
            - Django ImageField
            - image_url field

        Missing images are allowed.
        """

        image = getattr(
            self.product,
            "image",
            None,
        )

        if image:

            # Django ImageField
            try:
                return image.url

            except Exception:
                pass

        image_url = getattr(
            self.product,
            "image_url",
            None,
        )

        if image_url:
            return image_url

        return None

    # =========================================================
    # CLASSIFICATION
    # =========================================================

    def run_classification(
        self,
        ai_result,
    ):
        """
        Existing Classification module remains responsible
        for classification business logic/persistence.

        AI inference supplies:
            - predicted category
            - confidence
            - alternatives
            - other inference metadata

        The existing classification service is given the
        AI result whenever its interface supports it.

        IMPORTANT:
            This method does not replace the Classification
            module with Decision & Review.
        """

        try:

            from services.classification_service import (
                classify_product,
            )

            try:

                return classify_product(
                    self.product,
                    ai_result.to_dict(),
                )

            except TypeError:

                # Backward compatibility with the existing
                # two-argument/one-argument implementation.
                return classify_product(
                    self.product
                )

        except ImportError:

            # Existing fallback retained.
            return ai_result.to_dict()

    # =========================================================
    # ATTRIBUTES
    # =========================================================

    def run_attributes(
        self,
        classification_result,
        ai_result,
    ):
        """
        Existing Attributes module remains responsible
        for attribute persistence/business logic.

        AI extracted attributes are supplied as additional
        evidence.
        """

        try:

            from attributes.services import (
                extract_product_attributes,
            )

            try:

                return extract_product_attributes(
                    self.product,
                    classification_result,
                    ai_result.to_dict(),
                )

            except TypeError:

                return extract_product_attributes(
                    self.product,
                    classification_result,
                )

        except ImportError:

            # Existing AI attribute fallback.
            return [
                {
                    "name": attribute.name,
                    "value": attribute.value,
                    "confidence": (
                        attribute.confidence
                    ),
                }

                for attribute
                in ai_result.attributes
            ]

    # =========================================================
    # DECISION & REVIEW
    # =========================================================

    def run_decision(
        self,
        ai_result,
    ):
        """
        Convert the existing AI inference result into
        a Decision & Review result.

        IMPORTANT:
            The AI result itself is NOT modified.

        Decision policy:

            >= 0.85
                AUTO_APPROVED

            >= 0.60 and < 0.85
                NEEDS_REVIEW

            < 0.60
                MANUAL_REVIEW

            AI failure
                FAILED
        """

        ai_data = ai_result.to_dict()

        # -----------------------------------------------------
        # Build primary category representation.
        # -----------------------------------------------------

        primary_category = None

        predicted_category_id = getattr(
            ai_result,
            "predicted_category_id",
            None,
        )

        if predicted_category_id:

            primary_category = {
                "category_id": (
                    predicted_category_id
                ),
            }

        # -----------------------------------------------------
        # Get alternatives from AI result.
        #
        # Different AI implementations may expose this as
        # "alternatives" or "alternative_categories".
        # -----------------------------------------------------

        alternatives = ai_data.get(
            "alternatives",
            None,
        )

        if alternatives is None:

            alternatives = ai_data.get(
                "alternative_categories",
                [],
            )

        # -----------------------------------------------------
        # Run Decision & Review service.
        # -----------------------------------------------------

        decision_result = make_decision(
            primary_category=primary_category,

            confidence=getattr(
                ai_result,
                "confidence",
                0.0,
            ),

            alternatives=alternatives,

            inference_failed=(
                not getattr(
                    ai_result,
                    "success",
                    False,
                )
            ),
        )

        # -----------------------------------------------------
        # Persist Decision & Review state.
        #
        # Classification has already run at this point.
        # -----------------------------------------------------

        self.persist_decision(
            ai_result,
            decision_result,
        )

        return decision_result

    # =========================================================
    # PERSIST DECISION
    # =========================================================

    def persist_decision(
        self,
        ai_result,
        decision_result,
    ):
        """
        Persist Decision & Review information.

        This creates/updates the DecisionReview record linked
        to the EXISTING ClassificationResult.

        The original AI prediction remains preserved.
        """

        from classification.models import (
            ClassificationResult,
        )

        from results.models import (
            DecisionReview,
        )

        # -----------------------------------------------------
        # Locate the ClassificationResult created by the
        # existing Classification module.
        # -----------------------------------------------------

        classification_result = (
            ClassificationResult.objects
            .filter(
                product=self.product
            )
            .order_by("-id")
            .first()
        )

        if not classification_result:

            # Do not invent a ClassificationResult here.
            #
            # Classification remains responsible for creating
            # its own result.
            #
            # This protects the existing architecture.
            return None

        ai_data = ai_result.to_dict()

        DecisionReview.objects.update_or_create(

            classification_result=(
                classification_result
            ),

            defaults={

                # Original AI result snapshot.
                "ai_prediction": ai_data,

                # Original AI confidence.
                "ai_confidence": (
                    getattr(
                        ai_result,
                        "confidence",
                        0.0,
                    )
                ),

                # Ranked alternatives produced by
                # Decision & Review.
                "ai_alternatives": (
                    decision_result.alternatives
                ),

                # Decision status.
                "decision_status": (
                    decision_result.status.value
                ),

                # Whether human review is required.
                "requires_review": (
                    decision_result.requires_review
                ),

                # Human-readable decision reason.
                "decision_reason": (
                    decision_result.reason
                ),
            },
        )

        return True

    # =========================================================
    # PERSIST TAXONOMY RESULT
    # =========================================================

    def persist_taxonomy_result(
        self,
        ai_result,
        decision_result=None,
    ):
        """
        Persist the taxonomy result.

        The taxonomy result continues to use the existing
        ProductTaxonomyResult model.

        Decision & Review is used as the source of truth
        for the decision status.
        """

        from taxonamy.models import (
            ProductTaxonomyResult,
        )

        category = None

        predicted_category_id = getattr(
            ai_result,
            "predicted_category_id",
            None,
        )

        if predicted_category_id:

            category = (
                TaxonomyCategory.objects
                .filter(
                    id=predicted_category_id,
                    is_archived=False,
                )
                .first()
            )

        ProductTaxonomyResult.objects.update_or_create(

            product=self.product,

            defaults={

                "category": category,

                "confidence": (
                    getattr(
                        ai_result,
                        "confidence",
                        0.0,
                    )
                ),

                "matched_text": (
                    getattr(
                        ai_result,
                        "matched_text",
                        "",
                    )
                ),

                "status": (
                    self._taxonomy_result_status(
                        ai_result,
                        decision_result,
                    )
                ),
            },
        )

    # =========================================================
    # TAXONOMY RESULT STATUS
    # =========================================================

    def _taxonomy_result_status(
        self,
        ai_result,
        decision_result=None,
    ):
        """
        Convert Decision & Review status into the existing
        taxonomy-result status values.

        Existing taxonomy statuses are retained:

            failed
            auto_approved
            needs_review
            manual_review
        """

        # -----------------------------------------------------
        # If Decision & Review already exists, use it.
        # -----------------------------------------------------

        if decision_result is not None:

            status = decision_result.status

            if status == DecisionStatus.FAILED:
                return "failed"

            if status == DecisionStatus.AUTO_APPROVED:
                return "auto_approved"

            if status == DecisionStatus.NEEDS_REVIEW:
                return "needs_review"

            if status == DecisionStatus.MANUAL_REVIEW:
                return "manual_review"

        # -----------------------------------------------------
        # Defensive fallback.
        #
        # This should normally only execute if the decision
        # service was not supplied.
        # -----------------------------------------------------

        if not getattr(
            ai_result,
            "success",
            False,
        ):
            return "failed"

        confidence = getattr(
            ai_result,
            "confidence",
            0.0,
        )

        if confidence >= 0.85:
            return "auto_approved"

        if confidence >= 0.60:
            return "needs_review"

        return "manual_review"

    # =========================================================
    # FINAL PROCESSING STATUS
    # =========================================================

    def update_final_status(
        self,
        ai_result,
        decision_result=None,
    ):
        """
        Update the Product processing status.

        Decision & Review is the source of truth for
        classification decision status.

        Mapping:

            AUTO_APPROVED
                -> COMPLETED

            NEEDS_REVIEW
                -> REVIEW

            MANUAL_REVIEW
                -> REVIEW

            FAILED
                -> FAILED
        """

        # -----------------------------------------------------
        # Prefer Decision & Review.
        # -----------------------------------------------------

        if decision_result is not None:

            status = decision_result.status

            if status == DecisionStatus.FAILED:

                self._set_status(
                    "FAILED"
                )

                return

            if status == DecisionStatus.AUTO_APPROVED:

                self._set_status(
                    "COMPLETED"
                )

                return

            if status in {
                DecisionStatus.NEEDS_REVIEW,
                DecisionStatus.MANUAL_REVIEW,
            }:

                self._set_status(
                    "REVIEW"
                )

                return

        # -----------------------------------------------------
        # Defensive fallback.
        #
        # Existing AI status behaviour remains available
        # if a decision result is unavailable.
        # -----------------------------------------------------

        if not getattr(
            ai_result,
            "success",
            False,
        ):

            self._set_status(
                "FAILED"
            )

            return

        confidence = getattr(
            ai_result,
            "confidence",
            0.0,
        )

        if confidence >= 0.85:

            self._set_status(
                "COMPLETED"
            )

        else:

            self._set_status(
                "REVIEW"
            )

    # =========================================================
    # DECISION SERIALIZATION
    # =========================================================

    def _decision_to_dict(
        self,
        decision_result,
    ):
        """
        Convert DecisionResult into a JSON-safe dictionary
        for the pipeline response.
        """

        if decision_result is None:
            return None

        return {
            "status": (
                decision_result.status.value
            ),

            "confidence": (
                decision_result.confidence
            ),

            "primary_category": (
                decision_result.primary_category
            ),

            "alternatives": (
                decision_result.alternatives
            ),

            "requires_review": (
                decision_result.requires_review
            ),

            "reason": (
                decision_result.reason
            ),
        }

    # =========================================================
    # PRODUCT STATUS
    # =========================================================

    def _set_status(
        self,
        status,
    ):
        """
        Update the Product processing status.

        Existing Product status handling is retained.
        """

        self.product.status = status

        self.product.updated_at = (
            timezone.now()
        )

        self.product.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
