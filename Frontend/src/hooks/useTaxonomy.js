import { useCallback, useState } from "react";

import {
  getTaxonomyCategories,
  searchTaxonomy,
  getProductTaxonomy,
  classifyProduct,
  bulkClassifyProducts,
} from "../api/taxonomy.api";

export function useTaxonomy() {
  const [categories, setCategories] = useState([]);
  const [searchResults, setSearchResults] = useState([]);

  const [productResult, setProductResult] =
    useState(null);

  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] =
    useState(false);
  const [classificationLoading, setClassificationLoading] =
    useState(false);

  const [error, setError] = useState(null);

  const loadCategories = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const data = await getTaxonomyCategories(filters);

        const results = Array.isArray(data)
          ? data
          : data?.results || [];

        setCategories(results);

        return results;
      } catch (err) {
        setError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const search = useCallback(async (query) => {
    if (!query?.trim()) {
      setSearchResults([]);
      return [];
    }

    setSearchLoading(true);
    setError(null);

    try {
      const data = await searchTaxonomy(
        query.trim()
      );

      const results = data?.results || [];

      setSearchResults(results);

      return results;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const loadProductTaxonomy = useCallback(
    async (productId) => {
      setLoading(true);
      setError(null);

      try {
        const data =
          await getProductTaxonomy(productId);

        setProductResult(data);

        return data;
      } catch (err) {
        setError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const runClassification = useCallback(
    async (productId) => {
      setClassificationLoading(true);
      setError(null);

      try {
        const data =
          await classifyProduct(productId);

        setProductResult(data);

        return data;
      } catch (err) {
        setError(err);
        throw err;
      } finally {
        setClassificationLoading(false);
      }
    },
    []
  );

  const runBulkClassification =
    useCallback(async (limit = null) => {
      setClassificationLoading(true);
      setError(null);

      try {
        return await bulkClassifyProducts(limit);
      } catch (err) {
        setError(err);
        throw err;
      } finally {
        setClassificationLoading(false);
      }
    }, []);

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

    clearSearchResults: () =>
      setSearchResults([]),

    clearError: () =>
      setError(null),
  };
}