
import { useLayoutEffect } from "react";

export function useRtl(element: HTMLElement | null) {
  useLayoutEffect(() => {
    if (element) {
      element.dir = "rtl";
      return () => {
        element.dir = "";
      };
    }
  }, [element]);
}
