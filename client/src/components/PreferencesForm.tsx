import React, { useContext, useState, useEffect } from "react";
import { PreferencesContext } from "../context/PreferencesContext";
import { getRecommendations } from "../services/api";
import LoadingSpinner from "./LoadingSpinner";
import "./PreferencesForm.css";

const CUISINE_OPTIONS = [
  { value: "None", label: "None" },
  { value: "american", label: "American" },
  { value: "italian", label: "Italian" },
  { value: "mexican", label: "Mexican" },
  { value: "chinese", label: "Chinese" },
  { value: "japanese", label: "Japanese" },
  { value: "indian", label: "Indian" },
  { value: "mediterranean", label: "Mediterranean" },
  { value: "thai", label: "Thai" },
  { value: "vietnamese", label: "Vietnamese" },
  { value: "korean", label: "Korean" },
];

const PreferencesForm: React.FC = () => {
  const { preferences, updatePreferences } = useContext(PreferencesContext);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isDragging, setIsDragging] = useState<"min" | "max" | null>(null);
  const [skippedMacros, setSkippedMacros] = useState<{
    protein: boolean;
    carbs: boolean;
    fats: boolean;
  }>({
    protein: false,
    carbs: false,
    fats: false,
  });

  useEffect(() => {
    let stepInterval: NodeJS.Timeout;
    if (loading) {
      stepInterval = setInterval(() => {
        setLoadingStep((prev) => (prev < 3 ? prev + 1 : prev));
      }, 2000);
    }
    return () => clearInterval(stepInterval);
  }, [loading]);

  const handleSkipMacro = (macro: "protein" | "carbs" | "fats") => {
    setSkippedMacros((prev) => ({
      ...prev,
      [macro]: !prev[macro],
    }));

    if (!skippedMacros[macro]) {
      // If we're skipping it now, clear the value
      updatePreferences({ [`${macro}Grams`]: undefined });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoadingStep(0);
    setError(null);
    setRecommendations([]);

    try {
      const apiPreferences = {
        allergies: preferences.allergies,
        calorie_count: Number(preferences.targetCalories),
        macronutrients: {
          protein_grams: skippedMacros.protein
            ? undefined
            : Number(preferences.proteinGrams),
          carbs_grams: skippedMacros.carbs
            ? undefined
            : Number(preferences.carbsGrams),
          fats_grams: skippedMacros.fats
            ? undefined
            : Number(preferences.fatsGrams),
        },
        zipcode: preferences.zipCode,
        cuisine_preferences:
          preferences.cuisines[0] === "None" ? [] : preferences.cuisines,
        price_range: [preferences.minPrice, preferences.maxPrice],
      };

      const response = await getRecommendations(apiPreferences);
      setRecommendations(response.recommendations);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to get recommendations. Please try again."
      );
      console.error("Error getting recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    if (name === "targetCalories") {
      if (value === "") {
        updatePreferences({
          targetCalories: undefined,
        });
        return;
      }

      const calories = parseInt(value) || 0;
      updatePreferences({
        targetCalories: calories,
      });
    } else {
      updatePreferences({ [name]: value });
    }
  };

  // Calculate recommended macros based on calories
  const calculateRecommendedMacros = () => {
    const calories = preferences.targetCalories || 0;
    const proteinCals = calories * 0.3; // 30% protein
    const carbsCals = calories * 0.4; // 40% carbs
    const fatsCals = calories * 0.3; // 30% fats

    return {
      protein: Math.round(proteinCals / 4),
      carbs: Math.round(carbsCals / 4),
      fats: Math.round(fatsCals / 9),
    };
  };

  const recommendedMacros = calculateRecommendedMacros();

  const handleAllergiesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const allergies = e.target.value
      .split(",")
      .map((allergy) => allergy.trim());
    updatePreferences({ allergies });
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    let numValue = Math.min(Math.max(parseInt(value) || 1, 1), 100);

    if (name === "minPrice") {
      numValue = Math.min(numValue, preferences.maxPrice - 1);
      updatePreferences({ minPrice: numValue });
    } else if (name === "maxPrice") {
      numValue = Math.max(numValue, preferences.minPrice + 1);
      updatePreferences({ maxPrice: numValue });
    }
  };

  const handleSliderMouseDown =
    (type: "min" | "max") => (e: React.MouseEvent) => {
      setIsDragging(type);
    };

  const handleSliderMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;

    const container = e.currentTarget as HTMLDivElement;
    const rect = container.getBoundingClientRect();
    const percent = Math.min(
      Math.max((e.clientX - rect.left) / rect.width, 0),
      1
    );
    const value = Math.round(percent * 49 + 1);

    if (isDragging === "min") {
      const newValue = Math.min(value, preferences.maxPrice - 1);
      updatePreferences({ minPrice: newValue });
    } else {
      const newValue = Math.max(value, preferences.minPrice + 1);
      updatePreferences({ maxPrice: newValue });
    }
  };

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(null);
    document.addEventListener("mouseup", handleMouseUp);
    return () => document.removeEventListener("mouseup", handleMouseUp);
  }, []);

  useEffect(() => {
    const range = document.querySelector(".slider-range") as HTMLElement;
    const minHandle = document.querySelector(".min-handle") as HTMLElement;
    const maxHandle = document.querySelector(".max-handle") as HTMLElement;

    if (range && minHandle && maxHandle) {
      const minPercent = ((preferences.minPrice - 1) / 49) * 100;
      const maxPercent = ((preferences.maxPrice - 1) / 49) * 100;

      range.style.left = `${minPercent}%`;
      range.style.width = `${maxPercent - minPercent}%`;

      minHandle.style.left = `${minPercent}%`;
      maxHandle.style.left = `${maxPercent}%`;
    }
  }, [preferences.minPrice, preferences.maxPrice]);

  const handleCuisineChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    if (selectedValue === "None") {
      updatePreferences({ cuisines: ["None"] });
    } else if (!preferences.cuisines.includes(selectedValue)) {
      const newCuisines =
        preferences.cuisines[0] === "None"
          ? [selectedValue]
          : [...preferences.cuisines, selectedValue];
      updatePreferences({ cuisines: newCuisines });
    }
    // Reset select value
    e.target.value = "";
  };

  const removeCuisine = (cuisineToRemove: string) => {
    const newCuisines = preferences.cuisines.filter(
      (c) => c !== cuisineToRemove
    );
    if (newCuisines.length === 0) {
      updatePreferences({ cuisines: ["None"] });
    } else {
      updatePreferences({ cuisines: newCuisines });
    }
  };

  return (
    <div className="preferences-form-container">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="targetCalories">Target Calories</label>
          <input
            type="number"
            id="targetCalories"
            name="targetCalories"
            value={
              preferences.targetCalories === undefined
                ? ""
                : preferences.targetCalories
            }
            onChange={handleInputChange}
            min="0"
            step="10"
            required
            placeholder="Enter target calories"
          />
        </div>

        <div className="form-group">
          <label htmlFor="proteinGrams">Protein (g)</label>
          <div className="input-with-skip">
            <input
              type="number"
              id="proteinGrams"
              name="proteinGrams"
              value={
                preferences.proteinGrams === undefined
                  ? ""
                  : preferences.proteinGrams
              }
              onChange={handleInputChange}
              min="0"
              required={!skippedMacros.protein}
              placeholder={
                preferences.targetCalories && !skippedMacros.protein
                  ? `Recommended: ${recommendedMacros.protein}g`
                  : "Enter protein in grams"
              }
              disabled={skippedMacros.protein}
            />
            <button
              type="button"
              onClick={() => handleSkipMacro("protein")}
              className={`skip-button ${
                skippedMacros.protein ? "skipped" : ""
              }`}
            >
              {skippedMacros.protein ? "Specify" : "Skip"}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="carbsGrams">Carbs (g)</label>
          <div className="input-with-skip">
            <input
              type="number"
              id="carbsGrams"
              name="carbsGrams"
              value={
                preferences.carbsGrams === undefined
                  ? ""
                  : preferences.carbsGrams
              }
              onChange={handleInputChange}
              min="0"
              required={!skippedMacros.carbs}
              placeholder={
                preferences.targetCalories && !skippedMacros.carbs
                  ? `Recommended: ${recommendedMacros.carbs}g`
                  : "Enter carbs in grams"
              }
              disabled={skippedMacros.carbs}
            />
            <button
              type="button"
              onClick={() => handleSkipMacro("carbs")}
              className={`skip-button ${skippedMacros.carbs ? "skipped" : ""}`}
            >
              {skippedMacros.carbs ? "Specify" : "Skip"}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="fatsGrams">Fats (g)</label>
          <div className="input-with-skip">
            <input
              type="number"
              id="fatsGrams"
              name="fatsGrams"
              value={
                preferences.fatsGrams === undefined ? "" : preferences.fatsGrams
              }
              onChange={handleInputChange}
              min="0"
              required={!skippedMacros.fats}
              placeholder={
                preferences.targetCalories && !skippedMacros.fats
                  ? `Recommended: ${recommendedMacros.fats}g`
                  : "Enter fats in grams"
              }
              disabled={skippedMacros.fats}
            />
            <button
              type="button"
              onClick={() => handleSkipMacro("fats")}
              className={`skip-button ${skippedMacros.fats ? "skipped" : ""}`}
            >
              {skippedMacros.fats ? "Specify" : "Skip"}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="allergies">
            Food Allergies (leave blank if none)
          </label>
          <input
            type="text"
            id="allergies"
            name="allergies"
            value={preferences.allergies.join(", ")}
            onChange={handleAllergiesChange}
            placeholder="e.g., peanuts, shellfish, dairy"
          />
        </div>

        <div className="form-group">
          <label htmlFor="zipCode">ZIP Code</label>
          <input
            type="text"
            id="zipCode"
            name="zipCode"
            value={preferences.zipCode}
            onChange={handleInputChange}
            pattern="[0-9]{5}"
            required
            placeholder="e.g., 46556"
          />
        </div>

        <div className="form-group">
          <label htmlFor="cuisine">Preferred Cuisines</label>
          <div className="cuisine-select-container">
            <div className="selected-cuisines">
              {preferences.cuisines.map((cuisine) => (
                <div key={cuisine} className="cuisine-tag">
                  {CUISINE_OPTIONS.find((opt) => opt.value === cuisine)?.label}
                  {cuisine !== "None" && (
                    <button
                      type="button"
                      onClick={() => removeCuisine(cuisine)}
                      className="remove-cuisine"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
            <select
              id="cuisine"
              name="cuisine"
              onChange={handleCuisineChange}
              value=""
              className="cuisine-select"
            >
              <option value="">Add a cuisine...</option>
              {CUISINE_OPTIONS.filter(
                (option) =>
                  !preferences.cuisines.includes(option.value) ||
                  option.value === "None"
              ).map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="priceRange">Price Range ($)</label>
          <div className="price-range-container">
            <div className="price-range-inputs">
              <input
                type="number"
                id="minPrice"
                name="minPrice"
                value={preferences.minPrice}
                onChange={handlePriceChange}
                min="1"
                max="49"
                className="price-input"
              />
              <span>to</span>
              <input
                type="number"
                id="maxPrice"
                name="maxPrice"
                value={preferences.maxPrice}
                onChange={handlePriceChange}
                min="2"
                max="50"
                className="price-input"
              />
            </div>
            <div
              className="price-range-slider-container"
              onMouseMove={handleSliderMouseMove}
            >
              <div className="slider-track"></div>
              <div className="slider-range"></div>
              <div
                className="slider-handle min-handle"
                onMouseDown={handleSliderMouseDown("min")}
              ></div>
              <div
                className="slider-handle max-handle"
                onMouseDown={handleSliderMouseDown("max")}
              ></div>
            </div>
            <div className="price-range-labels">
              <span>1</span>
              <span>50</span>
            </div>
          </div>
        </div>

        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? "Finding Restaurants..." : "Find Restaurants"}
        </button>
      </form>

      {loading && <LoadingSpinner currentStep={loadingStep} />}

      {error && <div className="error-message">{error}</div>}

      {!loading && recommendations.length > 0 && (
        <div className="recommendations">
          <h2>Recommended Restaurants</h2>
          {recommendations.map((rec, index) => (
            <div
              key={index}
              className={`recommendation-card ${
                rec.matches_all_targets ? "perfect-match" : ""
              }`}
            >
              <h3>{rec.restaurant_name}</h3>
              <p>{rec.address}</p>
              <p>
                <strong>Recommended Dish:</strong> {rec.dish_name}
              </p>
              <p>
                <strong>Calories:</strong> {rec.calories}
              </p>
              <p>
                <strong>Macros:</strong> Protein: {rec.macronutrients.protein}g,
                Carbs: {rec.macronutrients.carbs}g, Fats:{" "}
                {rec.macronutrients.fats}g
              </p>
              <p>
                <strong>Price:</strong> ${rec.price_range}
              </p>
              <p>
                <strong>Why:</strong> {rec.reason}
              </p>
              {rec.missing_targets && rec.missing_targets.length > 0 && (
                <div className="missing-targets">
                  <p>
                    <strong>Missing Targets:</strong>
                  </p>
                  <ul>
                    {rec.missing_targets.map((target: string, i: number) => (
                      <li key={i}>{target}</li>
                    ))}
                  </ul>
                </div>
              )}
              {rec.suggestions && rec.suggestions.length > 0 && (
                <div className="suggestions">
                  <p>
                    <strong>Suggestions to Meet Targets:</strong>
                  </p>
                  <ul>
                    {rec.suggestions.map((suggestion: string, i: number) => (
                      <li key={i}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PreferencesForm;
