import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from "react-native";
import { TevroxMobileEmptyState } from "@/components/ui/emptystate";
import { listAnalyses, type AnalysisItem } from "@/services/analysis";

function statusVariant(status: string): "verified" | "unverified" | "rejected" | "info" {
  switch (status) {
    case "completed":
      return "verified";
    case "fallback":
      return "unverified";
    case "failed":
      return "rejected";
    default:
      return "info";
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case "completed":
      return "Completed";
    case "fallback":
      return "Fallback";
    case "failed":
      return "Failed";
    default:
      return status;
  }
}

export default function AnalysisHistoryScreen() {
  const [items, setItems] = useState<AnalysisItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const handle = window.setTimeout(() => {
      setLoading(true);
      setError(null);
      listAnalyses({ limit: 50 })
        .then((data) => {
          if (!cancelled) {
            setItems(data.items);
          }
        })
        .catch((reason: unknown) => {
          if (!cancelled) {
            setError(reason instanceof Error ? reason.message : "Failed to load history");
          }
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 0);

    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loading}>Loading analyses…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Analysis History</Text>
      <Text style={styles.subtitle}>
        {items.length} analysis{items.length === 1 ? "" : "s"}
      </Text>

      {items.length === 0 && (
        <Text>No items</Text>
      )}

      {items.length > 0 && (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <Text key={item.id}>
              Analysis #{item.id.slice(0, 8)}
            </Text>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F9FAFB",
    padding: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#18181b",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: "#6B7280",
    marginBottom: 16,
  },
  loading: {
    fontSize: 16,
    color: "#6B7280",
    marginTop: 40,
  },
  error: {
    fontSize: 14,
    color: "#EF4444",
    marginTop: 40,
    textAlign: "center",
  },
});
