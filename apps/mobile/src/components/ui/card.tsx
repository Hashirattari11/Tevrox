import React from "react";
import { StyleSheet, TouchableOpacity } from "react-native";

export interface TevroxMobileCardProps {
  /** Card children */
  children: React.ReactNode;
  /** On press handler */
  onPress?: () => void;
  /** Elevated shadow level */
  elevation?: "none" | "sm" | "md" | "lg";
  /** Background color */
  background?: string;
  /** Additional styles */
  style?: any;
}

export function TevroxMobileCard({
  children,
  onPress,
  elevation = "md",
  background = "#FFFFFF",
  style,
}: TevroxMobileCardProps) {
  const elevationStyles = {
    none: { elevation: 0 },
    sm: { elevation: 1 },
    md: { elevation: 3 },
    lg: { elevation: 5 },
  }[elevation];

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={onPress ? 0.8 : undefined}
      style={[
        styles.card,
        elevationStyles,
        { backgroundColor: background },
        { borderWidth: 1, borderColor: "#E5E7EB" },
        style,
      ]}
    >
      {children}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
});