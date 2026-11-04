import { Platform } from "react-native";

// Android emulator reaches the host machine through 10.0.2.2; physical devices need LAN IP.
export const apiBaseUrl = process.env.EXPO_PUBLIC_API_URL || (Platform.OS === "android" ? "http://10.0.2.2:8000" : "http://localhost:8000");
