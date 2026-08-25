import {
  useEffect,
  useState,
} from "react";

import { useParams } from "react-router-dom";

import { useTaxonomy } from "../../hooks/useTaxonomy";

import LoadingState from "../../components/common/LoadingState";
import ErrorState from "../../components/common/ErrorState";


function getStatusClasses(status) {

  switch (status) {

    case "classified":
      return "bg-green-100 text-green-700";

    case "review":
      return "bg-yellow-100 text-yellow-700";

    case "failed":
      return "bg-red-100 text-red-700";

    case "pending":
    default:
      return "bg-gray-100 text-gray-700";
  }
}


export default function ClassificationPage() {

  const { id } =
    useParams();

  const {
    productResult,
    loading,
    classificationLoading,
    error,
    loadProductTaxonomy,
    runClassification,
  } = useTaxonomy();

  const [actionError, setActionError] =
    useState(null);


  useEffect(() => {

    if (id) {
      loadProductTaxonomy(id);
    }

  }, [
    id,
    loadProductTaxonomy,
  ]);


  const handleClassify =
    async () => {

      setActionError(null);

      try {

        await runClassification(id);

      } catch (err) {

        setActionError(err);
      }
    };


  if (loading) {

    return (
      <LoadingState
        message="Loading classification..."
      />
    );
  }


  if (
    error &&
    error.status === 404
  ) {

    return (

      <div className="space-y-4">

        <div>

          <h1 className="text-2xl font-bold text-gray-900">
            Classification
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Product #{id}
          </p>

        </div>


        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6">

          <h2 className="font-semibold text-yellow-900">
            Product has not been classified
          </h2>

          <p className="mt-1 text-sm text-yellow-800">
            Run the classification service to generate
            a taxonomy result.
          </p>


          <button
            type="button"
            onClick={handleClassify}
            disabled={classificationLoading}
            className="mt-4 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {classificationLoading
              ? "Classifying..."
              : "Run Classification"}
          </button>

        </div>


        {actionError && (

          <ErrorState
            message={
              actionError?.message ||
              "Classification failed."
            }
          />

        )}

      </div>

    );
  }


  if (error) {

    return (

      <ErrorState
        message={
          error?.message ||
          "Failed to load classification."
        }
        onRetry={() =>
          loadProductTaxonomy(id)
        }
      />

    );
  }


  if (!productResult) {

    return (

      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">

        No classification result available.

      </div>

    );
  }


  const category =
    productResult.category;


  /*
   * Backend confidence is already 0-100.
   *
   * DO NOT multiply by 100.
   */

  const confidence =
    Number(
      productResult.confidence || 0
    );

  const confidencePercentage =
    Math.min(
      Math.round(confidence),
      100
    );


  return (

    <div className="space-y-6">

      {/* HEADER */}

      <div>

        <h1 className="text-2xl font-bold text-gray-900">
          Product Classification
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Product #{productResult.product}
        </p>

      </div>


      {/* MAIN */}

      <div className="grid gap-6 lg:grid-cols-2">


        {/* CATEGORY */}

        <section className="rounded-lg border border-gray-200 bg-white p-6">

          <div className="flex items-start justify-between">

            <div>

              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Predicted Category
              </p>

              <h2 className="mt-2 text-xl font-semibold text-gray-900">

                {category?.name ||
                  "No category assigned"}

              </h2>

            </div>


            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusClasses(
                productResult.status
              )}`}
            >

              {productResult.status ||
                "pending"}

            </span>

          </div>


          {category?.full_name && (

            <div className="mt-6">

              <p className="text-xs text-gray-500">
                Complete Taxonomy Path
              </p>

              <p className="mt-2 rounded-md bg-gray-50 p-3 text-sm text-gray-800">

                {category.full_name}

              </p>

            </div>

          )}


          {category?.level !==
            undefined &&
            category?.level !==
            null && (

              <div className="mt-4">

                <p className="text-xs text-gray-500">
                  Taxonomy Level
                </p>

                <p className="mt-1 font-medium text-gray-900">
                  Level {category.level}
                </p>

              </div>

            )}


          {category?.shopify_id && (

            <div className="mt-4">

              <p className="text-xs text-gray-500">
                Shopify Category ID
              </p>

              <p className="mt-1 font-mono text-sm font-medium text-gray-900">
                {category.shopify_id}
              </p>

            </div>

          )}

        </section>


        {/* CONFIDENCE */}

        <section className="rounded-lg border border-gray-200 bg-white p-6">

          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Confidence
          </p>


          <div className="mt-4 flex items-end gap-3">

            <span className="text-4xl font-bold text-gray-900">

              {confidencePercentage}%

            </span>

            <span className="pb-1 text-sm text-gray-500">
              confidence
            </span>

          </div>


          <div className="mt-4 h-3 overflow-hidden rounded-full bg-gray-200">

            <div
              className="h-full rounded-full bg-gray-900 transition-all"
              style={{
                width: `${confidencePercentage}%`,
              }}
            />

          </div>


          <div className="mt-6">

            <p className="text-xs text-gray-500">
              Matched Product Text
            </p>

            <p className="mt-2 max-h-48 overflow-auto rounded-md bg-gray-50 p-3 text-sm leading-6 text-gray-800">

              {productResult.matched_text ||
                "No matched text available."}

            </p>

          </div>

        </section>

      </div>


      {/* ACTIONS */}

      <section className="rounded-lg border border-gray-200 bg-white p-6">

        <h2 className="font-semibold text-gray-900">
          Classification Actions
        </h2>


        <button
          type="button"
          onClick={handleClassify}
          disabled={classificationLoading}
          className="mt-4 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >

          {classificationLoading
            ? "Classifying..."
            : "Re-run Classification"}

        </button>


        {actionError && (

          <div className="mt-4">

            <ErrorState
              message={
                actionError?.message ||
                "Classification failed."
              }
            />

          </div>

        )}

      </section>

    </div>

  );
}