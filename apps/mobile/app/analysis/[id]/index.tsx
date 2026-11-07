import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from "react-native";
import { router } from "expo-router";
import { TevroxMobileCard } from "@/components/ui/card";
import { TevroxMobileBadge } from "@/components/ui/badge";
import { TevroxMobileButton } from "@/components/ui/button";
import { getAnalysis, deleteAnalysis, type AnalysisItem } from "@/services/analysis";

function cautionVariant(level: string): "verified" | "unverified" | "rejected" | "info" {
  switch (level) {
    case "caution":
      return "rejected";
    case "note":
      return "unverified";
    default:
      return "info";
  }
}

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

export default function AnalysisReportScreen() {
  const { params } = router as any;
  const id = params?.id;
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;

    const handle = window.setTimeout(() => {
      setLoading(true);
      setError(null);
      getAnalysis(id)
        .then((data) => {
          if (!cancelled) setItem(data);
        })
        .catch((reason: unknown) => {
          if (!cancelled) {
            setError(reason instanceof Error ? reason.message : "Could not load report");
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
  }, [id]);

  const handleDelete = async () => {
    Alert.alert(
      "Delete",
      "Delete this analysis?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await deleteAnalysis(id);
              router.push("/analysis");
            } catch (e: any) {
              Alert.alert("Error", e.message);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loading}>Loading report…</Text>
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

  if (!item) {
    return (
      <View style={styles.container}>
        <Text style={styles.loading}>Report not found.</Text>
      </View>
    );
  }

  const result = item.result;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Analysis Report</Text>

      {item.product_unverified && (
        <TevroxMobileCard style={styles.card}>
          <Text style={styles.cardTitle}>Unverified product</Text>
          <Text style={styles.muted}>
            This product&apos;s ingredient list has not been verified yet.
          </Text>
        </TevroxMobileCard>
      )}

      <TevroxMobileCard style={styles.card}>
        <Text style={styles.cardTitle}>Summary</Text>
        <Text style={styles.cardText}>{result.summary}</Text>
      </TevroxMobileCard>

      <TevroxMobileCard style={styles.card}>
        <Text style={styles.cardTitle}>Suitability for Your Skin</Text>
        <Text style={styles.cardText}>{result.suitability_overview}</Text>
        <Text style={styles.meta}>
          Confidence: {result.confidence} &bull; {result.confidence_reason}
        </Text>
      </TevroxMobileCard>

      <TevroxMobileCard style={styles.card}>
        <Text style={styles.cardTitle}>Details</Text>
        <Text style={styles.meta}>Model: {item.model_used}</Text>
        <Text style={styles.meta}>Status: {item.status}</Text>
        <Text style={styles.meta}>Prompt version: {item.prompt_version ?? "\u2014"}</Text>
        <Text style={styles.meta}>Rules version: {item.rules_version ?? "\u2014"}</Text>
        {item.latency_ms != null && (
          <Text style={styles.meta}>Latency: {item.latency_ms} ms</Text>
        )}
      </TevroxMobileCard>

      <Text style={styles.sectionTitle}>Key Ingredients</Text>
      {result.key_ingredients.length === 0 ? (
        <Text style={styles.muted}>No ingredients parsed.</Text>
      ) : (
        result.key_ingredients.map((ing: any) => (
          <TevroxMobileCard key={ing.ingredient_id} style={styles.ingredientCard}>
            <Text style={styles.ingredientName}>{ing.name}</Text>
            <Text style={styles.ingredientRole}>{ing.role}</Text>
            <Text style={styles.ingredientText}>{ing.explanation}</Text>
            <TevroxMobileBadge
              text={ing.caution_level}
              status={cautionVariant(ing.caution_level)}
            />
          </TevroxMobileCard>
        ))
      )}

      {result.cautions.length > 0 && (
        <Text style={styles.sectionTitle}>Cautions</Text>
      )}
      {result.cautions.map((c: string, i: number) => (
        <TevroxMobileCard key={i} style={styles.cautionCard}>
          <Text style={styles.cautionText}>{c}</Text>
        </TevroxMobileCard>
      ))}

      <Text style={styles.sectionTitle}>Limitations</Text>
      {result.limitations.map((l: string, i: number) => (
        <TevroxMobileCard key={i} style={styles.limitationCard}>
          <Text style={styles.limitationText}>{l}</Text>
        </TevroxMobileCard>
      ))}

      <TevroxMobileCard style={styles.disclaimerCard}>
        <Text style={styles.disclaimerTitle}>Important Disclaimer</Text>
        <Text style={styles.disclaimerText}>
          Tevrox provides educational information about cosmetic ingredients.
          It is not medical advice and does not diagnose or treat any
          condition. If you have skin concerns or a reaction, talk to a
          qualified professional.
        </Text>
      </TevroxMobileCard>

      <TouchableOpacity
        onPress={handleDelete}
        style={styles.deleteButton}
      >
        <Text style={styles.deleteText}>Delete analysis</Text>
      </TouchableOpacity>
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
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#18181b",
    marginBottom: 8,
  },
  cardText: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 20,
  },
  meta: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
  muted: {
    fontSize: 14,
    color: "#6B7280",
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#18181b",
    marginTop: 16,
    marginBottom: 8,
  },
  ingredientCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  ingredientName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#18181b",
  },
  ingredientRole: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 2,
  },
  ingredientText: {
    fontSize: 12,
    color: "#374151",
    marginTop: 4,
    lineHeight: 18,
  },
  cautionCard: {
    backgroundColor: "#FEF3C7",
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
  },
  cautionText: {
    fontSize: 14,
    color: "#92400E",
    lineHeight: 18,
  },
  limitationCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  limitationText: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 18,
  },
  disclaimerCard: {
    backgroundColor: "#FEF2F2",
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
    borderWidth: 1,
    borderColor: "#FECACA",
  },
  disclaimerTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#991B1B",
    marginBottom: 8,
  },
  disclaimerText: {
    fontSize: 14,
    color: "#991B1B",
    lineHeight: 20,
  },
  deleteButton: {
    backgroundColor: "#EF4444",
    borderRadius: 8,
    padding: 12,
    alignItems: "center",
    marginTop: 16,
  },
  deleteText: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "600",
  },
});
