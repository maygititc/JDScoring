// Check if the JD is valid based on the analysis result
const isValidJD = (result) => {
  // Consider it valid if the confidence is above a threshold (e.g., 50%)
  return result.is_valid_jd && result.confidence >= 50;
};

// In the render function:
{analysisResult && (
  <div className="mt-4 p-4 bg-gray-100 rounded-md">
    <h3 className="text-lg font-medium">Analysis Result</h3>
    <p>Valid Job Description: {analysisResult.is_valid_jd ? "Yes" : "No"}</p>
    <p>Confidence: {analysisResult.confidence.toFixed(1)}%</p>
    
    {isValidJD(analysisResult) ? (
      <>
        <p className="font-medium mt-2">Overview:</p>
        <p>{analysisResult.overview}</p>
        <button
          onClick={handleGenerateQuestions}
          className="mt-4 py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700"
          disabled={isGeneratingQuestions}
        >
          {isGeneratingQuestions ? "Generating Questions..." : "Generate Interview Questions"}
        </button>
      </>
    ) : (
      <p className="text-red-600 mt-2">
        This text doesn't appear to be a valid job description or has low confidence. Please try with a different text.
      </p>
    )}
  </div>
)} 