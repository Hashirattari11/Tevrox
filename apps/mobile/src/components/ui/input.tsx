import React from "react";
import { StyleSheet, TextInput, View, Text } from "react-native";

export interface TevroxMobileInputProps {
  /** Input label */
  label?: string;
  /** Input placeholder */
  placeholder?: string;
  /** Input value */
  value?: string;
  /** On change handler */
  onChangeText: (text: string) => void;
  /** Whether input is disabled */
  disabled?: boolean;
  /** Whether input is required */
  required?: boolean;
  /** Keyboard type */
  keyboardType?: "default" | "email-address" | "numeric";
  /** Whether input is multiline */
  multiline?: boolean;
  /** Number of lines (for multiline) */
  numberOfLines?: number;
  /** Input error message */
  error?: string;
  /** Secure text entry (for passwords) */
  secureTextEntry?: boolean;
}

export function TevroxMobileInput({
  label,
  placeholder = "",
  value,
  onChangeText,
  required = false,
  keyboardType = "default",
  multiline,
  numberOfLines,
  secureTextEntry = false,
  error,
  ...props
}: TevroxMobileInputProps) {
  return (
    <View style={styles.container}>
      {label && (
        <Text style={styles.label}>{label}{required && <Text style={styles.requiredAsterisk}>*</Text>}</Text>
      )}
      <TextInput
        value={value ?? ""}
        onChangeText={onChangeText}
        keyboardType={keyboardType}
        secureTextEntry={secureTextEntry}
        style={styles.input}
        placeholder={placeholder}
        accessibilityLabel={label}
        multiline={multiline}
        numberOfLines={numberOfLines}
        {...props}
      />
      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 4,
  },
  requiredAsterisk: {
    color: "#EF4444",
    marginLeft: 2,
    fontSize: 12,
  },
  input: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 14,
    fontSize: 14,
    color: "#18181b",
  },
  errorText: {
    color: "#EF4444",
    fontSize: 10,
    marginTop: 4,
  },
});