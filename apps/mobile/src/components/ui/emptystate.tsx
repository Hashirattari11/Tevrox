import React from "react";
import { StyleSheet, View, Text, TouchableOpacity, Image } from "react-native";

export interface TevroxMobileEmptyStateProps {
  /** Title text */
  title: string;
  /** Subtitle text */
  subtitle?: string;
  /** Description text */
  description?: string;
  /** Action button text */
  actionLabel?: string;
  /** On action press */
  onAction?: () => void;
  /** Icon source (require) */
  iconSource?: any;
  /** Icon style width */
  iconWidth?: number;
  /** Icon style height */
  iconHeight?: number;
}

export function TevroxMobileEmptyState({
  title,
  subtitle,
  description,
  actionLabel,
  onAction,
  iconSource,
  iconWidth = 40,
  iconHeight = 40,
}: TevroxMobileEmptyStateProps) {
  return (
    <View style={styles.container}>
      <Image source={iconSource} style={[styles.icon, { width: iconWidth, height: iconHeight }]} />
      <Text style={styles.title}>{title}</Text>
      {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      {description && <Text style={styles.description}>{description}</Text>}
      {actionLabel && onAction && (
        <TouchableOpacity
          onPress={onAction}
          style={styles.actionButton}
          accessible={true}
          accessibilityLabel={actionLabel}
        >
          <Text style={styles.actionButtonText}>{actionLabel}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignContent: "center",
    padding: 40,
    textAlign: "center",
  },
  icon: {
    marginBottom: 20,
    resizeMode: "contain",
  },
  title: {
    fontSize: 18,
    fontWeight: "600",
    color: "#18181b",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: "#6B7280",
    marginBottom: 12,
  },
  description: {
    fontSize: 13,
    color: "#9CA3AF",
    marginBottom: 20,
  },
  actionButton: {
    backgroundColor: "#219EBC",
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  actionButtonText: {
    color: "white",
    fontSize: 14,
    fontWeight: "600",
    textAlign: "center",
  },
});