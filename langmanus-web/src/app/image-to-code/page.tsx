"use client";
import { useState, useRef } from "react";

export default function ImageToFrontend() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState("");
  const fileInputRef = useRef<unknown>(null); // To reset file input

  // It's good practice to put API URLs in environment variables
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  const resetStateForNewUpload = () => {
    setError(null);
    setSuccessMessage("");
    // setIsLoading(false); // isLoading is specific to an active request
  };

  const handleImageSelection = (file: File) => {
    if (file && file.type.startsWith("image/")) {
      // Check for file size (example: 10MB limit)
      const maxSizeInBytes = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSizeInBytes) {
        setError(
          `File is too large (${(file.size / 1024 / 1024).toFixed(2)} MB). Maximum size is 10MB.`,
        );
        setSelectedImage(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = ""; // Reset file input
        }
        return;
      }
      setSelectedImage(file);
      resetStateForNewUpload();
    } else if (file) {
      setError("Invalid file type. Please upload an image (PNG, JPG, GIF).");
      setSelectedImage(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = ""; // Reset file input
      }
    }
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    handleImageSelection(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isLoading) return; // Don't allow drag interactions during loading
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isLoading) return;
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      handleImageSelection(file);
    }
  };

  const handleGenerateFrontendClick = async () => {
    if (!selectedImage || isLoading) return;

    setIsLoading(true);
    setError(null);
    setSuccessMessage("");

    const formData = new FormData();
    formData.append("file", selectedImage);

    try {
      const response = await fetch(`${API_BASE_URL}/generate-frontend/`, {
        method: "POST",
        body: formData,
        // 'Content-Type': 'multipart/form-data' is automatically set by browser for FormData
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = downloadUrl;
        // Try to get a filename from content-disposition or default
        const contentDisposition = response.headers.get("content-disposition");
        let filename = "generated_frontend.zip";
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
          if (filenameMatch && filenameMatch.length === 2)
            filename = filenameMatch[1];
        } else {
          filename =
            selectedImage.name.replace(/\.[^/.]+$/, "") + "_frontend.zip";
        }
        a.download = filename;

        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);

        setSuccessMessage(
          "Frontend code generated! Download should have started.",
        );
        // Optionally clear the selection after successful generation
        // setSelectedImage(null);
        // if (fileInputRef.current) {
        //   fileInputRef.current.value = "";
        // }
      } else {
        let errorDetail = `Error ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json(); // FastAPI often returns JSON errors
          if (errorData && errorData.detail) {
            errorDetail =
              typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
          }
        } catch (e) {
          // If parsing JSON fails, use the text of the response
          const textError = await response.text();
          if (textError) errorDetail = textError;
          console.warn("Could not parse error response as JSON.");
        }
        setError(errorDetail);
        console.error("API Error Response:", errorDetail);
      }
    } catch (err) {
      console.error("Frontend Network/Fetch Error:", err);
      setError(
        err.message ||
          "Network error or server is unreachable. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearSelection = () => {
    setSelectedImage(null);
    setError(null);
    setSuccessMessage("");
    if (fileInputRef.current) {
      fileInputRef.current.value = ""; // Resets the file input
    }
  };

  return (
    <div
      className="flex min-h-screen w-full flex-col items-center"
      style={{ backgroundColor: "rgb(248, 247, 245)" }}
    >
      {/* Header Section */}
      <header className="relative flex w-full items-center justify-between px-6 pb-8 pt-6">
        {/* Logo Section - Ensure logo.png is in your public folder */}
        <div className="left-4 top-4 z-50 h-16 w-16 overflow-hidden rounded-lg bg-white shadow-lg">
          <img
            src="/logo.png"
            alt="Logo"
            className="h-full w-full object-contain p-1" // object-contain might be better for logos
          />
        </div>
        {/* Title */}
        <div>
          <a
            href="/"
            className="inline-flex w-full transform cursor-pointer items-center justify-center rounded-lg bg-blue-600 px-6 py-3 font-bold text-white shadow-md transition-all duration-200 hover:-translate-y-0.5 hover:bg-blue-700 hover:shadow-lg md:w-auto"
          >
            Text to code
          </a>
        </div>
      </header>

      <div>
        <h1 className="mb-2 text-center text-4xl font-bold text-gray-800 md:text-5xl">
          Generate Image to Frontend
        </h1>
        <p className="mx-auto mb-4 max-w-2xl text-center text-xl font-bold text-gray-500">
          Upload your image and transform it into beautiful frontend code.
        </p>
      </div>

      {/* Main Content */}
      <main className="mx-auto w-full max-w-2xl px-6 pb-12">
        <div
          className="rounded-2xl p-6 shadow-xl md:p-8"
          style={{ backgroundColor: "rgb(255, 255, 255)" }}
        >
          {/* Upload Area */}
          <div
            className={`relative rounded-xl border-2 border-dashed p-8 text-center transition-all duration-300 ease-in-out md:p-12 ${
              isLoading
                ? "cursor-not-allowed border-gray-300 bg-gray-100"
                : dragActive
                  ? "scale-105 border-blue-500 bg-blue-50"
                  : selectedImage
                    ? "border-green-400 bg-green-50"
                    : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png, image/jpeg, image/gif" // Be more specific
              onChange={handleImageUpload}
              className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
              id="image-upload"
              disabled={isLoading}
            />

            {selectedImage && !isLoading && (
              <div className="space-y-3">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 ring-4 ring-green-200">
                  <svg
                    className="h-8 w-8 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <div>
                  <p className="text-lg font-semibold text-gray-800">
                    Image Selected
                  </p>
                  <p
                    className="mt-1 w-full truncate px-2 text-gray-700"
                    title={selectedImage.name}
                  >
                    {selectedImage.name}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    Size: {(selectedImage.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={handleClearSelection}
                  className="mt-2 text-sm font-medium text-red-600 hover:text-red-800"
                  disabled={isLoading}
                >
                  Clear Selection
                </button>
              </div>
            )}

            {!selectedImage && !isLoading && (
              <div className="space-y-3">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 ring-4 ring-gray-200">
                  <svg
                    className="h-8 w-8 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </div>
                <div>
                  <label
                    htmlFor="image-upload"
                    className="cursor-pointer font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Upload your image
                  </label>
                  <p className="mt-1 text-sm text-gray-600">
                    Drag & drop or click to browse
                  </p>
                  <p className="mt-2 text-xs text-gray-500">
                    PNG, JPG, GIF up to 10MB
                  </p>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-blue-600"></div>
                <p className="text-lg font-medium text-gray-700">
                  Generating Frontend...
                </p>
                <p className="text-sm text-gray-500">
                  This may take a few moments.
                </p>
              </div>
            )}
          </div>

          {/* Error and Success Messages */}
          {error && (
            <div className="mt-4 rounded-md border border-red-400 bg-red-100 p-3 text-sm text-red-700">
              <strong className="font-bold">Error:</strong> {error}
            </div>
          )}
          {successMessage && (
            <div className="mt-4 rounded-md border border-green-400 bg-green-100 p-3 text-sm text-green-700">
              <strong className="font-bold">Success:</strong> {successMessage}
            </div>
          )}

          {/* Action/Upload Button Area */}
          <div className="mt-6 flex flex-col items-center space-y-4">
            {!selectedImage && !isLoading && (
              <label
                htmlFor="image-upload"
                className="inline-flex w-full transform cursor-pointer items-center justify-center rounded-lg bg-blue-600 px-8 py-3 font-bold text-white shadow-md transition-all duration-200 hover:-translate-y-0.5 hover:bg-blue-700 hover:shadow-lg md:w-auto"
              >
                <svg
                  className="mr-2 h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
                Choose Image
              </label>
            )}

            {selectedImage && (
              <button
                onClick={handleGenerateFrontendClick}
                disabled={isLoading || !selectedImage}
                className={`inline-flex w-full transform items-center justify-center rounded-lg px-8 py-3 font-medium shadow-md transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg md:w-auto ${
                  isLoading
                    ? "cursor-not-allowed bg-gray-400 text-gray-700"
                    : "bg-gradient-to-r from-green-500 to-blue-600 text-white hover:from-green-600 hover:to-blue-700"
                }`}
              >
                {isLoading ? (
                  <>
                    <svg
                      className="-ml-1 mr-3 h-5 w-5 animate-spin text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg
                      className="mr-2 h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                    Generate Frontend
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
