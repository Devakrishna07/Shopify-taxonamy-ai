function ScoreBar({ label, value }) {
  if (value === null || value === undefined) {
    return null;
  }

  const numericValue = Number(value);
  const percentage = Math.max(
    0,
    Math.min(100, numericValue * 100)
  );

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-gray-700">
          {label}
        </span>

        <span className="font-semibold text-gray-900">
          {percentage.toFixed(1)}%
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-indigo-600 transition-all"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}

export default function ClassificationScores({
  confidence,
  textScore,
  imageScore,
  attributeScore,
}) {
  return (
    <div className="space-y-5">
      <ScoreBar
        label="Overall Confidence"
        value={confidence}
      />

      <ScoreBar
        label="Text Score"
        value={textScore}
      />

      <ScoreBar
        label="Image Score"
        value={imageScore}
      />

      <ScoreBar
        label="Attribute Score"
        value={attributeScore}
      />
    </div>
  );
}