import React, { useEffect, useRef, useState } from "react";
import { loadGoogleMaps } from "../utils/loadGoogleMaps";

// The API key should be loaded from environment variables
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

interface RestaurantMapProps {
  address: string;
  restaurantName: string;
}

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
    .replace(/\s*State Hwy\s*/i, " State Highway ")
    .replace(/\s*Dr\s*/i, " Drive ")
    .replace(/\s*Ln\s*/i, " Lane ")
    .replace(/\s*Ct\s*/i, " Court ")
    .trim();

  // Ensure USA is not included as it can sometimes confuse the geocoder
  normalized = normalized.replace(/,?\s*USA$/i, "");

  return normalized;
};

const formatAddress = (address: string): string => {
  const normalizedAddress = normalizeAddress(address);

  // Check if the address already contains state and ZIP code
  const hasStateAndZip = /[A-Z]{2}\s+\d{5}(-\d{4})?/.test(normalizedAddress);

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
  const geocoderRef = useRef<google.maps.Geocoder | null>(null);

  useEffect(() => {
    let isMounted = true;

    const initMap = async () => {
      try {
        await loadGoogleMaps();

        if (!isMounted || !mapRef.current) return;

        // Initialize geocoder if not already initialized
        if (!geocoderRef.current) {
          geocoderRef.current = new window.google.maps.Geocoder();
        }

        const formattedAddress = formatAddress(address);
        console.log(`Attempting to geocode address: ${formattedAddress}`);

        const attemptGeocoding = (retryCount: number = 0) => {
          if (!geocoderRef.current) return;

          geocoderRef.current.geocode(
            {
              address: formattedAddress,
              region: "us",
              bounds: new window.google.maps.LatLngBounds(
                new window.google.maps.LatLng(24.396308, -125.0), // SW - covers continental US
                new window.google.maps.LatLng(49.384358, -66.93457) // NE
              ),
            },
            (results, status) => {
              if (!isMounted) return;

              if (status === "OK" && results && results[0]) {
                const location = results[0].geometry.location;
                console.log(
                  `Successfully geocoded: ${results[0].formatted_address}`
                );

                if (!mapInstanceRef.current && mapRef.current) {
                  mapInstanceRef.current = new window.google.maps.Map(
                    mapRef.current,
                    {
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
                    }
                  );
                } else if (mapInstanceRef.current) {
                  mapInstanceRef.current.setCenter(location);
                }

                if (markerRef.current) {
                  markerRef.current.setMap(null);
                }

                markerRef.current = new window.google.maps.Marker({
                  map: mapInstanceRef.current,
                  position: location,
                  title: restaurantName,
                  animation: window.google.maps.Animation.DROP,
                });

                setIsLoading(false);
                setError(null);
              } else {
                console.error(
                  `Geocoding failed for address: ${formattedAddress}, status: ${status}`
                );

                // If we haven't exceeded retry attempts and it's a retryable error
                if (
                  retryCount < 3 &&
                  (status === "OVER_QUERY_LIMIT" ||
                    status === "ZERO_RESULTS" ||
                    status === "UNKNOWN_ERROR")
                ) {
                  setTimeout(
                    () => attemptGeocoding(retryCount + 1),
                    1000 * Math.pow(2, retryCount) // Exponential backoff
                  );
                } else {
                  setError(
                    `Unable to load map location. Please check the address.`
                  );
                  setIsLoading(false);
                }
              }
            }
          );
        };

        attemptGeocoding();
      } catch (err) {
        if (!isMounted) return;
        console.error("Map initialization error:", err);
        setError("Failed to load map. Please try refreshing the page.");
        setIsLoading(false);
      }
    };

    initMap();

    // Cleanup function
    return () => {
      isMounted = false;
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
