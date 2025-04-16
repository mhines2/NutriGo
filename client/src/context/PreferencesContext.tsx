import React, { createContext, useContext, useState, ReactNode } from "react";

interface Preferences {
  targetCalories: number | undefined;
  proteinGrams: number | undefined;
  carbsGrams: number | undefined;
  fatsGrams: number | undefined;
  allergies: string[];
  zipCode: string;
  cuisines: string[];
  minPrice: number;
  maxPrice: number;
}

interface PreferencesContextType {
  preferences: Preferences;
  updatePreferences: (updates: Partial<Preferences>) => void;
}

const defaultPreferences: Preferences = {
  targetCalories: undefined,
  proteinGrams: undefined,
  carbsGrams: undefined,
  fatsGrams: undefined,
  allergies: [],
  zipCode: "",
  cuisines: ["None"],
  minPrice: 10,
  maxPrice: 25,
};

export const PreferencesContext = createContext<PreferencesContextType>({
  preferences: defaultPreferences,
  updatePreferences: () => {},
});

interface PreferencesProviderProps {
  children: ReactNode;
}

export const PreferencesProvider: React.FC<PreferencesProviderProps> = ({
  children,
}) => {
  const [preferences, setPreferences] =
    useState<Preferences>(defaultPreferences);

  const updatePreferences = (updates: Partial<Preferences>) => {
    setPreferences((prev) => ({
      ...prev,
      ...updates,
    }));
  };

  return (
    <PreferencesContext.Provider value={{ preferences, updatePreferences }}>
      {children}
    </PreferencesContext.Provider>
  );
};

// Custom hook
export const usePreferences = (): PreferencesContextType => {
  const context = useContext(PreferencesContext);
  if (context === undefined) {
    throw new Error("usePreferences must be used within a PreferencesProvider");
  }
  return context;
};
