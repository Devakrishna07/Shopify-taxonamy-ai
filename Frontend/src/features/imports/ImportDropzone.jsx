import { useRef, useState } from "react";

import {
  ACCEPTED_FILE_TYPES,
  formatFileSize,
  validateSelectedFile,
} from "./imports.utils";

export default function ImportDropzone({
  selectedFile,
  onFileSelected,
  disabled = false,
}) {
  const inputRef = useRef(null);

  const [dragActive, setDragActive] =
    useState(false);

  const [errors, setErrors] =
    useState([]);

  function processFile(file) {
    const validationErrors =
      validateSelectedFile(file);

    setErrors(validationErrors);

    if (validationErrors.length > 0) {
      onFileSelected(null);
      return;
    }

    onFileSelected(file);
  }

  function handleInputChange(event) {
    const file =
      event.target.files?.[0];

    if (file) {
      processFile(file);
    }

    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();

    setDragActive(false);

    if (disabled) {
      return;
    }

    const file =
      event.dataTransfer.files?.[0];

    if (file) {
      processFile(file);
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();

    if (!disabled) {
      setDragActive(true);
    }
  }

  function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();

    setDragActive(false);
  }

  function openFileDialog() {
    if (!disabled) {
      inputRef.current?.click();
    }
  }

  function handleKeyDown(event) {
    if (
      event.key === "Enter" ||
      event.key === " "
    ) {
      event.preventDefault();
      openFileDialog();
    }
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_FILE_TYPES.join(",")}
        onChange={handleInputChange}
        className="hidden"
        disabled={disabled}
      />

      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-disabled={disabled}
        onClick={openFileDialog}
        onKeyDown={handleKeyDown}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={[
          "rounded-xl border-2 border-dashed p-10 text-center transition",
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-slate-300 bg-white hover:border-slate-400",
          disabled
            ? "cursor-not-allowed opacity-60"
            : "cursor-pointer",
        ].join(" ")}
      >
        <div className="mx-auto max-w-md">
          <div className="mb-4 text-4xl">
            ↑
          </div>

          <h3 className="text-lg font-semibold text-slate-900">
            Upload product data
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Drag and drop your product file
            here, or click to browse.
          </p>

          <p className="mt-2 text-xs text-slate-400">
            Supported formats: CSV and XLSX
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Maximum file size: 20 MB
          </p>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="font-medium text-red-800">
            File validation failed
          </p>

          <ul className="mt-2 list-disc pl-5 text-sm text-red-700">
            {errors.map(
              (error, index) => (
                <li key={`${error}-${index}`}>
                  {error}
                </li>
              )
            )}
          </ul>
        </div>
      )}

      {selectedFile && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="font-medium text-slate-900">
                {selectedFile.name}
              </p>

              <p className="mt-1 text-sm text-slate-500">
                {formatFileSize(
                  selectedFile.size
                )}
              </p>
            </div>

            <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
              Ready
            </span>
          </div>
        </div>
      )}
    </div>
  );
}