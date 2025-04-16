declare global {
  interface Window {
    initMap: () => void;
  }
}

const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

export const loadGoogleMaps = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    console.log(
      "Environment variables available:",
      Object.keys(process.env).filter((key) => key.startsWith("REACT_APP_"))
    );
    console.log(
      "Attempting to load Google Maps with API key:",
      GOOGLE_MAPS_API_KEY ? "Key exists" : "No key found"
    );

    if (window.google && window.google.maps) {
      console.log("Google Maps already loaded");
      resolve();
      return;
    }

    if (!GOOGLE_MAPS_API_KEY) {
      console.error("Google Maps API key missing from environment variables");
      reject(new Error("Google Maps API key is not configured"));
      return;
    }

    window.initMap = () => {
      console.log("Google Maps initialization callback triggered");
      resolve();
    };

    const script = document.createElement("script");
    const scriptUrl = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&callback=initMap`;
    script.src = scriptUrl;
    script.async = true;
    script.defer = true;

    script.addEventListener("load", () => {
      console.log("Google Maps script loaded successfully");
    });

    script.onerror = (error) => {
      console.error("Failed to load Google Maps script:", error);
      console.error(
        "Attempted script URL:",
        scriptUrl.replace(GOOGLE_MAPS_API_KEY, "API_KEY_HIDDEN")
      );
      reject(new Error("Failed to load Google Maps script"));
    };

    document.head.appendChild(script);
    console.log("Google Maps script tag added to document");
  });
};

export default loadGoogleMaps;
