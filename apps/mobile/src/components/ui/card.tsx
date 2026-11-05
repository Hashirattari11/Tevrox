import React from "react";
import { StyleSheet, View, TouchableOpacity } from "react-native";

export interface TevroxMobileCardProps {
  /** Card children */
  children: React.ReactNode;
  /** On press handler */
  onPress?: () => void;
  /** Elevated shadow level */
  elevation?: "none" | "sm" | "md" | "lg";
  /** Background color */
  background?: string;
}

export function TevroxMobileCard({
  children,
  onPress,
  elevation = "md",
  background = "#FFFFFF",
}: TevroxMobileCardProps) {
  const elevationStyles = {
    none: { elevation: 0 },
    sm: { elevation: 1 },
    md: { elevation: 3 },
    lg: { elevation: 5 },
  }[elevation];

  return (
    <View
      style={[
        styles.card,
        elevationStyles,
        { backgroundColor: background },
        { borderWidth: 1, borderColor: "#E5E7EB" },
      ]}
      onPress={onPress}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
});