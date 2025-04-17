declare global {
  interface Window {
    google: any;
    initMap: () => void;
  }
}

const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

// Keep track of loading state
let loadingPromise: Promise<void> | null = null;

export const loadGoogleMaps = (): Promise<void> => {
  // If already loaded, return resolved promise
  if (window.google && window.google.maps) {
    return Promise.resolve();
  }

  // If currently loading, return the existing promise
  if (loadingPromise) {
    return loadingPromise;
  }

  // Create new loading promise
  loadingPromise = new Promise((resolve, reject) => {
    if (!GOOGLE_MAPS_API_KEY) {
      console.error("Google Maps API key missing from environment variables");
      reject(new Error("Google Maps API key is not configured"));
      return;
    }

    // Create a unique callback name
    const callbackName = "initMap_" + Math.random().toString(36).substr(2, 9);
    (window as any)[callbackName] = () => {
      delete (window as any)[callbackName];
      resolve();
    };

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&callback=${callbackName}`;
    script.async = true;
    script.defer = true;

    script.addEventListener("load", () => {
      console.log("Google Maps script loaded successfully");
    });

    script.onerror = (error) => {
      console.error("Failed to load Google Maps script:", error);
      loadingPromise = null; // Reset loading promise on error
      delete (window as any)[callbackName];
      reject(new Error("Failed to load Google Maps script"));
    };

    document.head.appendChild(script);
  });

  return loadingPromise;
};

export default loadGoogleMaps;
