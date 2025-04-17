export interface UserPreferences {
  allergies: string[];
  calorie_count: number;
  macronutrients: {
    protein_grams?: number;
    carbs_grams?: number;
    fats_grams?: number;
  };
  zipcode: string;
  cuisine_preferences: string[];
  price_range: number[];
}

export interface Restaurant {
  name: string;
  formatted_address: string;
  rating: number;
  price_level: number;
  types: string[];
  opening_hours: {
    open_now: boolean;
  };
}

export interface Recommendation {
  restaurant_name: string;
  address: string;
  dish_name: string;
  calories: number;
  macronutrients: {
    protein: number;
    carbs: number;
    fats: number;
  };
  reason: string;
  price_range: string;
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  error?: string;
}

export interface ApiStatus {
  status: string;
  openai_api: string;
  google_maps_api: string;
}
