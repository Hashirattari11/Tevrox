import * as React from "react";
import { ScrollView, View, Text, StatusBar } from "react-native";
import {
  TevroxButton,
  TevroxInput,
  TevroxCard,
  TevroxBadge,
  TevroxEmptyState,
  TevroxSkeleton,
  TevroxErrorState,
  TevroxPageHeader,
} from "@/components/ui";
import { Search as RCSearch } from "lucide-react";

export default function DevComponents() {
  return (
    <StatusBar light />
    <ScrollView
      contentContainerStyle={
        { flexGrow: 1, padding: 24, backgroundColor: "#F9FAFB" }
      }
    >
      <TevroxPageHeader title="Component Showcase" subtitle="All UI components" />

      {/* Button variants */}
      <View style={{ marginBottom: 24 }}>
        <Text style={{ fontSize: 16, fontWeight: "600", marginBottom: 8 }}>Button Variants</Text>
        <View style={{ flexDirection: "wrap", gap: 8 }}>
          <TevroxButton variant="primary" size="md">
            Primary
          </TevroxButton>
          <TevroxButton variant="secondary" size="md">
            Secondary
          </TevroxButton>
          <TevroxButton variant="ghost" size="md">
            Ghost
          </TevroxButton>
          <TevroxButton variant="danger" size="md">
            Danger
          </TevroxButton>
        </View>
      </View>

      {/* Input with error */}
      <TevroxInput
        label="Email input"
        placeholder="Enter email"
        error="Please enter a valid email"
        required
      />

      {/* Chip */}
      <TevroxChip selected>Selected Chip</TevroxChip>

      {/* Card */}
      <TevroxCard>
        <Text>This is a card with some content inside.</Text>
      </TevroxCard>

      {/* Badge */}
      <View style={{ marginTop: 16, flexDirection: "row", gap: 8 }}>
        <TevroxBadge status="verified">Verified</TevroxBadge>
        <TevroxBadge status="unverified">Unverified</TevroxBadge>
        <TevroxBadge status="rejected">Rejected</TevroxBadge>
        <TevroxBadge status="info">Info</TevroxBadge>
      </View>

      {/* Skeleton loader */}
      <View style={{ marginTop: 16, gap: 8 }}>

        <TevroxSkeleton width="100%" height="1rem" />
        <TevroxSkeleton width="100%" height="1.5rem" lines={3} />
        <TevroxSkeleton circle />
      </View>

      {/* Empty state */}
      <TevroxEmptyState
        title="No products yet"
        subtitle="Add your first product to get started"
        description="Products you search for will appear here."
        actionLabel="Add Product"
        onAction={() => alert("Add product clicked")}
        iconSource={RCSearch}
      />

      {/* Error state */}
      <TevroxErrorState
        title="Connection timeout"
        message="The server took too long to respond. Please try again."
        retryLabel="Retry"
        onRetry={() => alert("Retry clicked")}
        actionLabel="Contact support"
        onAction={() => alert("Support clicked")}
      />
    </ScrollView>
  );
}