import {
  useCallback,
  useState,
} from "react";

import {
  getProductTaxonomy,
  getProductTaxonomyResults,
  getTaxonomyStats,

  classifyProduct,
  bulkClassifyProducts,

  approveProductTaxonomy,
  rejectProductTaxonomy,
} from "../api/taxonomy.api";


export function useTaxonomy() {
  const [products, setProducts] =
    useState([]);

  const [productResult, setProductResult] =
    useState(null);

  const [stats, setStats] =
    useState(null);

  const [productsLoading, setProductsLoading] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [classificationLoading, setClassificationLoading] =
    useState(false);

  const [error, setError] =
    useState(null);


  const loadProductTaxonomyList =
    useCallback(
      async (params = {}) => {
        setProductsLoading(true);
        setError(null);

        try {
          const response =
            await getProductTaxonomyResults(
              params
            );

          const data =
            response?.data || response;

          setProducts(
            data?.results || []
          );

          return data;

        } catch (err) {
          setError(
            err?.response?.data ||
            err
          );

          throw err;

        } finally {
          setProductsLoading(false);
        }
      },
      []
    );


  const loadProductTaxonomy =
    useCallback(
      async (productId) => {
        setLoading(true);
        setError(null);

        try {
          const response =
            await getProductTaxonomy(
              productId
            );

          const data =
            response?.data || response;

          setProductResult(data);

          return data;

        } catch (err) {
          setError(
            err?.response?.data ||
            err
          );

          throw err;

        } finally {
          setLoading(false);
        }
      },
      []
    );


  const loadStats =
    useCallback(
      async () => {
        try {
          const response =
            await getTaxonomyStats();

          const data =
            response?.data || response;

          setStats(data);

          return data;

        } catch (err) {
          throw err;
        }
      },
      []
    );


  const runClassification =
    useCallback(
      async (productId) => {
        setClassificationLoading(
          true
        );
        setError(null);

        try {
          const response =
            await classifyProduct(
              productId
            );

          const data =
            response?.data || response;

          setProductResult(data);

          return data;

        } catch (err) {
          setError(
            err?.response?.data ||
            err
          );

          throw err;

        } finally {
          setClassificationLoading(
            false
          );
        }
      },
      []
    );


  const runBulkClassification =
    useCallback(
      async (
        limit = 10
      ) => {
        setClassificationLoading(
          true
        );
        setError(null);

        try {
          const response =
            await bulkClassifyProducts({
              limit,
              onlyUnclassified: true,
            });

          const data =
            response?.data || response;

          return data;

        } catch (err) {
          setError(
            err?.response?.data ||
            err
          );

          throw err;

        } finally {
          setClassificationLoading(
            false
          );
        }
      },
      []
    );


  const approveTaxonomy =
    useCallback(
      async (
        productId,
        categoryId
      ) => {
        const response =
          await approveProductTaxonomy(
            productId,
            categoryId
          );

        const data =
          response?.data || response;

        setProductResult(data);

        return data;
      },
      []
    );


  const rejectTaxonomy =
    useCallback(
      async (
        productId,
        reason
      ) => {
        const response =
          await rejectProductTaxonomy(
            productId,
            reason
          );

        const data =
          response?.data || response;

        setProductResult(data);

        return data;
      },
      []
    );


  return {
    products,
    productResult,
    stats,

    productsLoading,
    loading,
    classificationLoading,
    error,

    loadProductTaxonomyList,
    loadProductTaxonomy,
    loadStats,

    runClassification,
    runBulkClassification,

    approveTaxonomy,
    rejectTaxonomy,
  };
}
