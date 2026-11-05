import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { useAuth } from "@/src/components/AuthProvider";
import { TevroxBottomTabNavigator } from "@/components/navigation/bottom-tabs";
import { TevroxMobileButton } from "@/components/ui/button";
import { TevroxMobileInput } from "@/components/ui/input";
import { TevroxMobileCard } from "@/components/ui/card";
import { TevroxMobileBadge } from "@/components/ui/badge";
import { TevroxMobileEmptyState } from "@/components/ui/emptystate";

export default function MobileDashboard() {
  const { user, isAdmin, loading } = useAuth();

  if (loading || !user) {
    return null;
  }

  // Feature registry
  const features = [
    { key: "dashboard", label: "Dashboard", enabled: true, route: "/dashboard" },
    { key: "products", label: "Products", enabled: true, route: "/products" },
    { key: "analysis", label: "Analysis", enabled: false, route: "/analysis" },
    { key: "compare", label: "Compare", enabled: false, route: "/compare" },
    { key: "routines", label: "Routines", enabled: false, route: "/routines" },
    { key: "nutrition", label: "Nutrition", enabled: false, route: "/nutrition" },
  ];

  const recentlyViewed = ["prod-123", "prod-456"]; // Mock local data

  return (
    <>
      <TevroxBottomTabNavigator screen="home" />
      <View style={{ flex: 1, padding: 24, backgroundColor: "#F9FAFB" }}>
        <Text style={{ fontSize: 28, fontWeight: "700", color: "#18181b", marginBottom: 8 }}>
          Welcome, {user.name || "User"}
        </Text>

        {/* Profile completion prompt */}
        <TevroxMobileCard className={styles.profileCard} style={styles.container}>
          <Text style={styles.profileTitle}>Complete your profile</Text>
          <Text style={styles.profileSubtitle}>
            Add your skin type and concerns to get personalized recommendations
          </Text>
          <TevroxMobileInput
            label="Skin type"
            placeholder="e.g., Normal, Oily, Dry, Combination, Sensitive"
            onChangeText={() => {}}
            disabled
          />
          <TevroxMobileInput
            label="Skin concerns"
            placeholder="e.g., Acne, Dryness, Aging, Hyperpigmentation"
            onChangeText={() => {}}
            disabled
            multiline
            numberOfLines={3}
          />
          <TevroxMobileButton
            title="Save Profile"
            onPress={() => alert("Profile saved!")}
            variant="primary"
          />
        </TevroxMobileCard>

        {/* Skin concerns summary */}
        <TevroxMobileCard className={styles.skinCard} style={styles.container}>
          <Text style={styles.skinTitle}>Skin Concerns</Text>
          <View style={styles.chipContainer}>
            {["Acne-prone", "Anti-aging", "Sensitive"].map((concern) => (
              <TevroxMobileBadge
                key={concern}
                text={concern}
                status="info"
              />
            ))}
          </View>
        </TevroxMobileCard>

        {/* Quick actions */}
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionGrid}>
          {features.map((feat) => (
            <TouchableOpacity
              key={feat.key}
              onPress={onFeaturePress(feat)}
              style={styles.actionBox}
              accessible={true}
              accessibilityLabel={feat.label}
            >
              <View style={styles.actionIconContainer}>
                <MaterialCommunityIcons
                  name=getIconName(feat.key)
                  size={28}
                  color="#219EBC"
                />
              </View>
              <Text style={styles.actionTitle}>{feat.label}</Text>
              {feat.enabled || (
                <TevroxMobileBadge
                  status="unverified"
                  style={styles.badgeWarning}
                >
                  Coming Soon
                </TevroxMobileBadge>
              )}
            </TouchableOpacity>
          ))}
        </View>

        {/* Recently viewed */}
        <TevroxMobileCard style={styles.container}>
          <Text style={styles.sectionTitle}>Recently Viewed</Text>
          {recentlyViewed.length > 0 ? (
            <View style={styles.chipContainer}>
              {recentlyViewed.map((id) => (
                <View key={id} style={styles.recentChip}>
                  <Text style={styles.recentChipText}>Product {id}</Text>
                </View>
              ))}
            </View>
          ) : (
            <Text style={styles.emptyStateText}>
              No recently viewed products
            </Text>
          )}
        </TevroxMobileCard>
      </View>
    </>
  );
}

function onFeaturePress(feat: any) {
  return () => {
    if (feat.enabled) {
      alert(`Opening ${feat.label}...`);
    } else {
      Alert.alert(
        "Coming Soon",
        `${feat.label} is not available yet. Stay tuned for updates!`
      );
    }
  };
}

function getIconName(key: string) {
  const map: any = {
    dashboard: "grid",
    products: "package",
    analysis: "trending-up",
    compare: "grid-3x3",
    routines: "calendar",
    nutrition: "salad",
  };
  return map[key] || "grid";
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F9FAFB",
  },
  profileCard: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  profileTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#18181b",
    marginBottom: 4,
  },
  profileSubtitle: {
    fontSize: 14,
    color: "#6B7280",
    marginBottom: 16,
  },
  skinCard: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  skinTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#18181b",
    marginBottom: 12,
  },
  chipContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#374151",
    marginTop: 20,
    marginBottom: 12,
  },
  actionGrid: {
    gap: 12,
    marginBottom: 20,
  },
  actionBox: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 20,
    alignItems: "center",
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 1,
    width: "48%",
  },
  actionIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: "#F0F4F8",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 12,
    fontWeight: "600",
    color: "#18181b",
    textAlign: "center",
  },
  badgeWarning: {
    marginLeft: 4,
  },
  emptyStateText: {
    color: "#6B7280",
    fontSize: 14,
    textAlign: "center",
    marginTop: 20,
  },
  recentChip: {
    backgroundColor: "#E5E7EB",
    borderRadius: 20,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 6,
    marginBottom: 6,
    minWidth: 50,
    textAlign: "center",
  },
  recentChipText: {
    fontSize: 10,
    color: "#374151",
  },
});