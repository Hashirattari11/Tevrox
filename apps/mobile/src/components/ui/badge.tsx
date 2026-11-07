import React from "react";
import { StyleSheet, Text, TouchableOpacity } from "react-native";

export interface TevroxMobileBadgeProps {
  /** Badge text (used when children is not provided) */
  text?: string;
  /** Badge content (children) */
  children?: React.ReactNode;
  /** Badge status: verified, unverified, rejected, info */
  status?: "verified" | "unverified" | "rejected" | "info";
  /** On press handler */
  onPress?: () => void;
  /** Additional styles */
  style?: any;
}

const STATUS_BACKGROUND_COLORS: Record<string, string> = {
  verified: "#10B981",
  unverified: "#F59E0B",
  rejected: "#EF4444",
  info: "#6366F1",
};

export function TevroxMobileBadge({
  text,
  children,
  status = "info",
  onPress,
  style,
}: TevroxMobileBadgeProps) {
  const content = children ?? text;
  return (
    <TouchableOpacity
      onPress={onPress}
      accessible={true}
      accessibilityLabel={String(content ?? "")}
      style={[
        styles.badge,
        { backgroundColor: STATUS_BACKGROUND_COLORS[status] ?? STATUS_BACKGROUND_COLORS.info },
        style,
      ]}
    >
      <Text style={styles.badgeText}>{content}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  badge: {
    borderRadius: 9999,
    paddingHorizontal: 6,
    paddingVertical: 3,
    fontSize: 10,
    fontWeight: "600",
    color: "white",
    alignItems: "center",
    justifyContent: "center",
  },
  badgeText: {
    color: "white",
  },
});
