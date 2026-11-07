import { useEffect, useState } from "react";
import { SafeAreaView, StyleSheet, Text } from "react-native";
import { StatusCard } from "@/components/StatusCard";
import { getHealth } from "@/services/api";
import type { Health } from "@/types/health";

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getHealth().then(setHealth).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Backend unavailable")); }, []);
  return <SafeAreaView style={styles.page}><Text style={styles.kicker}>TEVROX · FOUNDATION</Text><Text style={styles.heading}>Skincare and nutrition, connected.</Text><StatusCard health={health} error={error} /></SafeAreaView>;
}

const styles = StyleSheet.create({ page: { flex: 1, padding: 24, paddingTop: 64, backgroundColor: "#f6f8f7" }, kicker: { color: "#047857", fontWeight: "700", letterSpacing: 2 }, heading: { marginTop: 18, fontSize: 32, fontWeight: "600", color: "#15302a" } });
