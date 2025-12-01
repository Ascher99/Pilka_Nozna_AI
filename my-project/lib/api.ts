import { PredictIn, PredictOut } from "@/types/predict";
import { API_BASE } from "./config";

export async function predictFastAPI(body: PredictIn): Promise<PredictOut> {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}
