import { apiRequest, DEMO_MODE } from "./client";

export async function getNotificationFeed() {
  if (DEMO_MODE) return null;
  try {
    return await apiRequest("/api/notifications");
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}
