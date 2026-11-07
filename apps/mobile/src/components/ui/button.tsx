import React from "react";
import { StyleSheet, TouchableOpacity, Text } from "react-native";

export interface TevroxMobileButtonProps {
  /** Button title */
  title: string;
  /** On press handler */
  onPress: () => void;
  /** Button variant: primary, secondary, danger */
  variant?: "primary" | "secondary" | "danger";
  /** Button size: sm, md, lg */
  size?: "sm" | "md" | "lg";
  /** Whether button is disabled */
  disabled?: boolean;
  /** Loading state */
  loading?: boolean;
  /** Accessibility label */
  accessibilityLabel?: string;
  /** Icon component (optional) */
  Icon?: React.ComponentType<{ size?: number; color?: string }>;
}

export function TevroxMobileButton({
  title,
  onPress,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  accessibilityLabel,
  Icon,
  ...props
}: TevroxMobileButtonProps) {
  const variantStyles = {
    primary: {
      backgroundColor: "#219EBC",
      paddingVertical: size === "sm" ? 6 : size === "md" ? 12 : 16,
      paddingHorizontal: size === "sm" ? 8 : size === "md" ? 16 : 24,
      borderRadius: size === "sm" ? 4 : size === "md" ? 8 : 12,
    },
    secondary: {
      backgroundColor: "transparent",
      borderWidth: 1,
      borderColor: "#D1D5DB",
      paddingVertical: size === "sm" ? 6 : size === "md" ? 12 : 16,
      paddingHorizontal: size === "sm" ? 8 : size === "md" ? 16 : 24,
      borderRadius: size === "sm" ? 4 : size === "md" ? 8 : 12,
    },
    danger: {
      backgroundColor: "#EF4444",
      paddingVertical: size === "sm" ? 6 : size === "md" ? 12 : 16,
      paddingHorizontal: size === "sm" ? 8 : size === "md" ? 16 : 24,
      borderRadius: size === "sm" ? 4 : size === "md" ? 8 : 12,
    },
  }[variant];

  const textColor = variant === "danger" ? "white" : "#18181b";

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      accessible={true}
      accessibilityLabel={accessibilityLabel || title}
      style={[styles.button, variantStyles, sizes[size]]}
      {...props}
    >
      {loading
        ? <Text style={styles.loadingText}>Loading...</Text>
        : <Text style={[styles.text, { color: textColor }]}>{title}</Text>}
      {Icon && <Icon size={20} color={textColor} />}
    </TouchableOpacity>
  );
}

const sizes = {
  sm: { paddingVertical: 6, paddingHorizontal: 8, borderRadius: 4 },
  md: { paddingVertical: 12, paddingHorizontal: 16, borderRadius: 8 },
  lg: { paddingVertical: 16, paddingHorizontal: 24, borderRadius: 12 },
};

const styles = StyleSheet.create({
  button: {
    elevation: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  loadingText: {
    color: "white",
  },
  text: {
    fontSize: 14,
    fontWeight: "600",
    textAlign: "center",
    color: "#18181b",
  },
});