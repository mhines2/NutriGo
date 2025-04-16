import React, { useEffect, useRef, useState } from "react";

// The API key should be loaded from environment variables
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

interface RestaurantMapProps {
  address: string;
  restaurantName: string;
}

const loadGoogleMapsScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (window.google && window.google.maps) {
      resolve();
      return;
    }

    if (!GOOGLE_MAPS_API_KEY) {
      reject(new Error("Google Maps API key is not configured"));
      return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}`;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () =>
      reject(new Error("Failed to load Google Maps script"));
    document.head.appendChild(script);
  });
};

const normalizeAddress = (address: string): string => {
  // Remove multiple spaces and normalize separators
  let normalized = address
    .replace(/\s+/g, " ")
    .replace(/,\s*/g, ", ")
    .replace(/\s*#\s*/g, " # ")
    .replace(/\s*Suite\s*/i, " Suite ")
    .replace(/\s*Ste\s*/i, " Suite ")
    .replace(/\s*Rd\s*/i, " Road ")
    .replace(/\s*St\s*/i, " Street ")
    .replace(/\s*Ave\s*/i, " Avenue ")
    .replace(/\s*Blvd\s*/i, " Boulevard ")
    .replace(/\s*Hwy\s*/i, " Highway ")
    .trim();

  // Ensure USA is not included as it can sometimes confuse the geocoder
  normalized = normalized.replace(/, USA$/, "");

  return normalized;
};

const formatAddress = (address: string): string => {
  const normalizedAddress = normalizeAddress(address);

  // Check if the address already contains state and ZIP code
  const hasStateAndZip = /[A-Z]{2}\s+\d{5}/.test(normalizedAddress);

  if (hasStateAndZip) {
    return normalizedAddress;
  }

  // Extract state and city if present
  const stateMatch = normalizedAddress.match(/,\s*([A-Z]{2})\s*$/);
  const cityMatch = normalizedAddress.match(/,\s*([^,]+),\s*[A-Z]{2}\s*$/);

  if (stateMatch && cityMatch) {
    // Address has city and state but no ZIP
    return normalizedAddress;
  }

  // If we don't have enough location information, return as is
  // The geocoder will handle it based on the region and bounds
  return normalizedAddress;
};

const RestaurantMap: React.FC<RestaurantMapProps> = ({
  address,
  restaurantName,
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.Marker | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initMap = async () => {
      try {
        await loadGoogleMapsScript();
        if (!mapRef.current) return;

        const geocoder = new google.maps.Geocoder();
        const formattedAddress = formatAddress(address);

        console.log(`Attempting to geocode address: ${formattedAddress}`);

        const attemptGeocoding = (retryCount: number = 0) => {
          geocoder.geocode(
            {
              address: formattedAddress,
              region: "us",
            },
            (results, status) => {
              if (status === "OK" && results && results[0]) {
                const location = results[0].geometry.location;
                console.log(
                  `Successfully geocoded: ${results[0].formatted_address}`
                );

                if (!mapInstanceRef.current && mapRef.current) {
                  mapInstanceRef.current = new google.maps.Map(mapRef.current, {
                    center: location,
                    zoom: 15,
                    mapTypeControl: false,
                    streetViewControl: false,
                    fullscreenControl: false,
                    styles: [
                      {
                        featureType: "poi",
                        elementType: "labels",
                        stylers: [{ visibility: "off" }],
                      },
                    ],
                  });
                } else if (mapInstanceRef.current) {
                  mapInstanceRef.current.setCenter(location);
                }

                if (markerRef.current) {
                  markerRef.current.setMap(null);
                }

                markerRef.current = new google.maps.Marker({
                  map: mapInstanceRef.current,
                  position: location,
                  title: restaurantName,
                  animation: google.maps.Animation.DROP,
                });

                setIsLoading(false);
                setError(null);
              } else {
                console.error(
                  `Geocoding failed for address: ${formattedAddress}, status: ${status}`
                );

                // If we haven't exceeded retry attempts and it's a retryable error
                if (
                  retryCount < 2 &&
                  (status === "OVER_QUERY_LIMIT" || status === "ZERO_RESULTS")
                ) {
                  setTimeout(
                    () => attemptGeocoding(retryCount + 1),
                    1000 * (retryCount + 1)
                  );
                } else {
                  setError(`Unable to load map location (${status})`);
                  setIsLoading(false);
                }
              }
            }
          );
        };

        attemptGeocoding();
      } catch (err) {
        console.error("Map initialization error:", err);
        setError(err instanceof Error ? err.message : "Failed to load map");
        setIsLoading(false);
      }
    };

    initMap();

    // Cleanup function
    return () => {
      if (markerRef.current) {
        markerRef.current.setMap(null);
      }
      if (mapInstanceRef.current) {
        // @ts-ignore
        mapInstanceRef.current = null;
      }
    };
  }, [address, restaurantName]);

  if (error) {
    return (
      <div
        style={{
          width: "100%",
          height: "200px",
          borderRadius: "0.75rem",
          backgroundColor: "#f8fafc",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#ef4444",
          fontSize: "0.875rem",
          marginTop: "1rem",
          padding: "1rem",
          textAlign: "center",
        }}
      >
        {error}
      </div>
    );
  }

  return (
    <div
      ref={mapRef}
      style={{
        width: "100%",
        height: "200px",
        borderRadius: "0.75rem",
        overflow: "hidden",
        marginTop: "1rem",
        opacity: isLoading ? 0.6 : 1,
        transition: "opacity 0.3s ease",
      }}
    />
  );
};

export default RestaurantMap;
