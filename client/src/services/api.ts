import axios from "axios";
import {
  Restaurant,
  UserPreferences,
  RecommendationsResponse,
  ApiStatus,
} from "../types";

const API_BASE_URL = "http://localhost:5001/api";

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// API functions
export const checkApiStatus = async (): Promise<ApiStatus> => {
  const response = await api.get<ApiStatus>("/status");
  return response.data;
};

export const getRestaurants = async (
  zipcode: string,
  radius: number = 5000
): Promise<Restaurant[]> => {
  const response = await api.get<Restaurant[]>("/restaurants", {
    params: { zipcode, radius },
  });
  return response.data;
};

export const getRecommendations = async (
  preferences: UserPreferences
): Promise<RecommendationsResponse> => {
  const response = await api.post<RecommendationsResponse>("/recommendations", {
    preferences,
  });
  return response.data;
};
