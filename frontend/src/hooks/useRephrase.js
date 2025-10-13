import { useCallback, useEffect, useMemo, useRef, useState } from "react";

export const STYLE_ORDER = ["professional", "casual", "polite", "social"];

export const STYLE_META = {
  professional: {
    label: "Professional",
    helper: "Confident and formal tone suitable for workspaces.",
  },
  casual: {
    label: "Casual",
    helper: "Conversational language that feels friendly and relaxed.",
  },
  polite: {
    label: "Polite",
    helper: "Respectful phrasing that stays considerate and neutral.",
  },
  social: {
    label: "Social media",
    helper: "Lively language crafted for timelines and captions.",
  },
};

const createEmptyOutputs = () => {
  const initial = {};
  STYLE_ORDER.forEach((style) => {
    initial[style] = "";
  });
  return initial;
};

export function useRephrase() {
  const [state, setState] = useState("idle");
  const [outputs, setOutputs] = useState(() => createEmptyOutputs());
  const [activeStyle, setActiveStyle] = useState(null);
  const eventSourceRef = useRef(null);
  const requestIdRef = useRef(null);

  const resetOutputs = useCallback(() => setOutputs(createEmptyOutputs()), []);

  const process = useCallback(
    async (text) => {
      setState("processing");
      resetOutputs();

      try {
        // Create rephrase request and get request_id
        const response = await fetch("/v1/rephrase", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            styles: STYLE_ORDER,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const { request_id } = await response.json();
        requestIdRef.current = request_id; // Store for cancel endpoint

        // Open SSE connection for streaming
        const eventSource = new EventSource(
          `/v1/rephrase/stream?request_id=${request_id}`
        );
        eventSourceRef.current = eventSource; // Store for cleanup

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === "delta") {
              setActiveStyle(data.style);
              setOutputs((prev) => ({
                ...prev,
                [data.style]: (prev[data.style] || "") + data.text,
              }));
            } else if (data.type === "error") {
              // Handle security error messages from backend
              setActiveStyle(null);
              setOutputs((prev) => ({
                ...prev,
                [data.style]: data.text, // Display the error message
              }));
            } else if (data.type === "complete") {
              // Style completed, but keep processing others
              setActiveStyle(null);
            } else if (data.type === "end") {
              setActiveStyle(null);
              setState("done");
              eventSource.close();
              eventSourceRef.current = null;
            }
          } catch (error) {
            console.error("Error parsing SSE data:", error);
          }
        };

        eventSource.onerror = (error) => {
          console.error("SSE error:", error);
          setActiveStyle(null);
          setState("canceled");
          eventSource.close();
          eventSourceRef.current = null;
        };
      } catch (error) {
        console.error("Error starting rephrase process:", error);
        setState("canceled");
        setActiveStyle(null);
      }
    },
    [resetOutputs]
  );

  const cancel = useCallback(async () => {
    // Close SSE connection if active
    if (
      eventSourceRef.current &&
      eventSourceRef.current instanceof EventSource
    ) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Note: Closing the EventSource will trigger request.is_disconnected() on
    // the backend, which will automatically close the OpenAI stream. The
    // explicit DELETE call below is not strictly necessary but provides a
    // faster cancellation signal and serves as a fallback in case the
    // disconnection is not detected immediately.
    if (requestIdRef.current) {
      try {
        await fetch(`/v1/rephrase/${requestIdRef.current}`, {
          method: "DELETE",
        });
        console.log(`Explicitly canceled request ${requestIdRef.current}`);
      } catch (error) {
        console.error("Error canceling request:", error);
      }
      requestIdRef.current = null;
    }

    setActiveStyle(null);
    setState("canceled");
  }, []);

  const reset = useCallback(() => {
    // Close any active SSE connection
    if (
      eventSourceRef.current &&
      eventSourceRef.current instanceof EventSource
    ) {
      eventSourceRef.current.close();
    }

    if (requestIdRef.current) {
      fetch(`/v1/rephrase/${requestIdRef.current}`, {
        method: "DELETE",
      }).catch((error) => {
        console.error("Error canceling request during reset:", error);
      });
    }

    eventSourceRef.current = null;
    requestIdRef.current = null;
    setActiveStyle(null);
    resetOutputs();
    setState("idle");
  }, [resetOutputs]);

  const isProcessing = state === "processing";

  const timeline = useMemo(
    () =>
      STYLE_ORDER.map((style) => ({
        style,
        label: STYLE_META[style].label,
        isActive: activeStyle === style,
        hasContent: outputs[style].trim().length > 0,
      })),
    [activeStyle, outputs]
  );

  useEffect(() => {
    // Cleanup function to close SSE connection on unmount
    return () => {
      if (
        eventSourceRef.current &&
        eventSourceRef.current instanceof EventSource
      ) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return {
    outputs,
    state,
    process,
    cancel,
    reset,
    isProcessing,
    activeStyle,
    timeline,
  };
}
