import React from "react";
import { useState, useEffect } from "react";
import { useNavigation, useProfile } from "@expo/router";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { StyleSheet, TabBarBottom, TabBarItem, SafeAreaView } from "expo-router";

export function TevroxBottomTabNavigator({
  screen,
}: { screen: string }) {
  const navigation = useNavigation();
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    const unsubscribe = navigation.addListener("focus", () => setIsFocused(true));
    return () => unsubscribe();
  }, []);

  const tabBarProps = {
    ariaLabel: "Main tab navigation",
    scrollEnabled: false,
    style: styles.tabBar,
  };

  const renderIcon = (name: string) => {
    const iconMap: any = {
      home: <MaterialCommunityIcons name="home" size={24} />,
      products: <MaterialCommunityIcons name="package" size={24} />,
      scan: <MaterialCommunityIcons name="qr-code" size={24} />,
      more: <MaterialCommunityIcons name="menu" size={24} />,
    };
    return iconMap[name] || <MaterialCommunityIcons name="home" size={24} />;
  };

  return (
    <SafeAreaView style={styles.container}>
      <TabBarBottom
        ariaLabel="Main tab navigation"
        type="default"
        allowFontScaling={false}
        style={styles.tabBar}
        selectedIndex={getTabIndex(screen)}
        onChange={(index) => navigation.replace(getRouteName(index))}
        {...tabBarProps}
      >
        <TabBarItem
          label="Home"
          accessible={true}
          accessibilityLabel="Home screen"
          icon={renderIcon("home")}
          testID="tab-home"
        />
        <TabBarItem
          label="Products"
          accessible={true}
          accessibilityLabel="Products screen"
          icon={renderIcon("products")}
          testID="tab-products"
        />
        <TabBarItem
          label="Scan"
          accessible={true}
          accessibilityLabel="Barcode scanner"
          icon={renderIcon("scan")}
          testID="tab-scan"
        />
        <TabBarItem
          label="More"
          accessible={true}
          accessibilityLabel="More options"
          icon={renderIcon("more")}
          testID="tab-more"
        />
      </TabBarBottom>
    </SafeAreaView>
  );
}

function getTabIndex(screen: string) {
  const mapping: any = {
    "home/:": 0,
    "products/:": 1,
    "scan/:": 2,
    "more/:": 3,
    "([a-zA-Z]+)/": 3, // Any other screen goes to More
  };
  for (const [pattern, index] of Object.entries(mapping)) {
    if (screen.startsWith(pattern)) return index;
  }
  return 3;
}

function getRouteName(index: number) {
  const mapping: any = [0, 1, 2, 3].map((i) => {
    switch (i) {
      case 0: return "home";
      case 1: return "products";
      case 2: return "scan";
      case 3: return "more";
    }
  });
  return mapping[index];
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  tabBar: {
    backgroundColor: "#F9FAFB",
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "#E5E5E5",
  },
});