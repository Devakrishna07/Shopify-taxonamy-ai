import {
  useCallback,
  useState,
} from "react";

import {
  getTaxonomyCategories,
  searchTaxonomy,
  getProductTaxonomy,
  classifyProduct,
  bulkClassifyProducts,
} from "../api/taxonomy.api";


export function useTaxonomy() {

  // ==========================================================
  // STATE
  // ==========================================================

  const [
    categories,
    setCategories,
  ] = useState([]);

  const [
    searchResults,
    setSearchResults,
  ] = useState([]);

  const [
    productResult,
    setProductResult,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    searchLoading,
    setSearchLoading,
  ] = useState(false);

  const [
    classificationLoading,
    setClassificationLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState(null);


  // ==========================================================
  // LOAD CATEGORIES
  // ==========================================================

  const loadCategories =
    useCallback(
      async (filters = {}) => {

        setLoading(true);
        setError(null);

        try {

          console.log(
            "[TAXONOMY] Loading categories",
            filters
          );

          const data =
            await getTaxonomyCategories(
              filters
            );

          /*
           * Django ListAPIView normally
           * returns:
           *
           * [
           *   {...},
           *   {...}
           * ]
           *
           * But pagination can return:
           *
           * {
           *   count: 100,
           *   results: [...]
           * }
           */

          const results =
            Array.isArray(data)
              ? data
              : Array.isArray(
                  data?.results
                )
              ? data.results
              : [];

          setCategories(
            results
          );

          console.log(
            "[TAXONOMY] Categories loaded:",
            results.length
          );

          return results;

        } catch (err) {

          console.error(
            "[TAXONOMY] Failed to load categories:",
            err
          );

          setError(err);

          return [];

        } finally {

          setLoading(false);
        }
      },
      []
    );


  // ==========================================================
  // SEARCH
  // ==========================================================

  const search =
    useCallback(
      async (query) => {

        const cleanQuery =
          query?.trim();

        if (!cleanQuery) {

          setSearchResults([]);

          return [];
        }

        setSearchLoading(true);
        setError(null);

        try {

          console.log(
            "[TAXONOMY] Searching:",
            cleanQuery
          );

          const data =
            await searchTaxonomy(
              cleanQuery
            );

          const results =
            Array.isArray(
              data?.results
            )
              ? data.results
              : Array.isArray(data)
              ? data
              : [];

          setSearchResults(
            results
          );

          console.log(
            "[TAXONOMY] Search results:",
            results.length
          );

          return results;

        } catch (err) {

          console.error(
            "[TAXONOMY] Search failed:",
            err
          );

          setError(err);

          setSearchResults([]);

          return [];

        } finally {

          setSearchLoading(false);
        }
      },
      []
    );


  // ==========================================================
  // GET PRODUCT TAXONOMY
  // ==========================================================

  const loadProductTaxonomy =
    useCallback(
      async (productId) => {

        setLoading(true);
        setError(null);

        try {

          const data =
            await getProductTaxonomy(
              productId
            );

          setProductResult(
            data
          );

          return data;

        } catch (err) {

          console.error(
            "[TAXONOMY] Failed to load product taxonomy:",
            err
          );

          setError(err);

          return null;

        } finally {

          setLoading(false);
        }
      },
      []
    );


  // ==========================================================
  // CLASSIFY PRODUCT
  // ==========================================================

  const runClassification =
    useCallback(
      async (productId) => {

        setClassificationLoading(
          true
        );

        setError(null);

        try {

          console.log(
            "[TAXONOMY] Classifying product:",
            productId
          );

          const data =
            await classifyProduct(
              productId
            );

          setProductResult(
            data
          );

          return data;

        } catch (err) {

          console.error(
            "[TAXONOMY] Classification failed:",
            err
          );

          setError(err);

          return null;

        } finally {

          setClassificationLoading(
            false
          );
        }
      },
      []
    );


  // ==========================================================
  // BULK CLASSIFICATION
  // ==========================================================

  const runBulkClassification =
    useCallback(
      async (limit = null) => {

        setClassificationLoading(
          true
        );

        setError(null);

        try {

          console.log(
            "[TAXONOMY] Starting bulk classification",
            {
              limit,
            }
          );

          return await bulkClassifyProducts(
            limit
          );

        } catch (err) {

          console.error(
            "[TAXONOMY] Bulk classification failed:",
            err
          );

          setError(err);

          return null;

        } finally {

          setClassificationLoading(
            false
          );
        }
      },
      []
    );


  // ==========================================================
  // CLEAR SEARCH
  // ==========================================================

  const clearSearchResults =
    useCallback(() => {

      setSearchResults([]);

    }, []);


  // ==========================================================
  // CLEAR ERROR
  // ==========================================================

  const clearError =
    useCallback(() => {

      setError(null);

    }, []);


  // ==========================================================
  // RETURN
  // ==========================================================

  return {

    categories,

    searchResults,

    productResult,

    loading,

    searchLoading,

    classificationLoading,

    error,

    loadCategories,

    search,

    loadProductTaxonomy,

    runClassification,

    runBulkClassification,

    clearSearchResults,

    clearError,
  };
}