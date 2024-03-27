import { useEffect, useRef } from 'react';

type CallbackFunction = () => void;

export default function useInterval(
  callback: CallbackFunction,
  delay: number
): void {
  const savedCallback = useRef<CallbackFunction>();

  // Remember the latest callback.
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval.
  useEffect(() => {
    function tick() {
      const callback = savedCallback.current;
      callback?.();
    }
    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}
