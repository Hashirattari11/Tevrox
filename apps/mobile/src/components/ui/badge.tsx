import React from "react";
import { StyleSheet, Text, View, TouchableOpacity } from "react-native";

export interface TevroxMobileBadgeProps {
  /** Badge text */
  text: string;
  /** Badge status: verified, unverified, rejected, info */
  status?: "verified" | "unverified" | "rejected" | "info";
  /** On press handler */
  onPress?: () => void;
}

export function TevroxMobileBadge({
  text,
  status,
  onPress,
}: TevroxMobileBadgeProps) {
  const statusStyles = {
    verified = {
      backgroundColor: "#10B981",
      color: "white",
    },
    unverified = {
      backgroundColor: "#F59E0B",
      color: "white",
    },
    rejected = {
      backgroundColor: "#EF4444",
      color: "white",
    },
    info = {
      backgroundColor: "#6366F1",
      color: "white",
    },
  }[status] || {
    backgroundColor: "#6B7280",
    color: "white",
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      accessible={true}
      accessibilityLabel={text}
      style={styles.badge}
    >
      <Text style={styles.badgeText}>{text}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  badge: {
    backgroundColor: (() => {
      switch (status) {
        case "verified":
          return "#10B981";
        case "unverified":
          return "#F59E0B";
        case "rejected":
          return "#EF4444";
        case "info":
          return "#6366F1";
        default:
          return "#6B7280";
      }
    })(),
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