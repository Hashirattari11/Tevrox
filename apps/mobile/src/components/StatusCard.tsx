import { StyleSheet, Text, View } from "react-native";
import type { Health } from "@/types/health";

export function StatusCard({ health, error }: { health: Health | null; error: string | null }) {
  return <View style={styles.card}><Text style={styles.title}>System status</Text>{health ? <><Text>Backend: {health.service} · {health.status} · v{health.version}</Text><Text>PostgreSQL: {health.database}</Text><Text>MongoDB: {health.mongodb}</Text></> : <Text>{error ?? "Loading status…"}</Text>}</View>;
}

const styles = StyleSheet.create({ card: { gap: 10, padding: 20, borderRadius: 16, backgroundColor: "#fff", marginTop: 24 }, title: { fontSize: 18, fontWeight: "600", color: "#15302a" } });
