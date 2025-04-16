import React from "react";
import "./LoadingSpinner.css";

interface LoadingSpinnerProps {
  currentStep: number;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ currentStep }) => {
  const steps = [
    "Finding restaurants in your area...",
    "Analyzing menu items and nutritional information...",
    "Matching with your dietary preferences...",
    "Generating personalized recommendations...",
  ];

  return (
    <div className="loading-container">
      <div className="loading-spinner" />
      <div className="loading-text">
        Please wait while we find the perfect restaurants for you
      </div>
      <div className="loading-steps">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`loading-step ${index <= currentStep ? "active" : ""}`}
          >
            {index <= currentStep ? "✓" : "○"} {step}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadingSpinner;
