import { useEffect, useState } from "react";

/** Phone-sized screens (the owner's UX review, step 4): the lab page becomes a reading mode there. */
export const PHONE_QUERY = "(max-width: 760px)";

export function usePhone(): boolean {
  const [phone, setPhone] = useState(() => typeof window !== "undefined" && window.matchMedia(PHONE_QUERY).matches);
  useEffect(() => {
    const mq = window.matchMedia(PHONE_QUERY);
    const on = () => setPhone(mq.matches);
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);
  return phone;
}
