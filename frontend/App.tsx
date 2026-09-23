import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? "não configurada";

export default function App() {
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.page}>
        <StatusBar style="light" />
        <View style={styles.card}>
          <Text style={styles.title}>Projeto pronto</Text>
          <Text style={styles.text}>Expo + Django + PostgreSQL</Text>
          <Text style={styles.label}>API</Text>
          <Text style={styles.code}>{apiUrl}</Text>
        </View>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    backgroundColor: "#111827",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  card: {
    width: "100%",
    maxWidth: 720,
    backgroundColor: "#1f2937",
    borderRadius: 18,
    padding: 28,
  },
  title: {
    color: "#f9fafb",
    fontSize: 30,
    fontWeight: "700",
    marginBottom: 8,
  },
  text: {
    color: "#d1d5db",
    fontSize: 18,
    marginBottom: 24,
  },
  label: {
    color: "#9ca3af",
    fontSize: 13,
    marginBottom: 6,
  },
  code: {
    color: "#f9fafb",
    fontFamily: "monospace",
  },
});
