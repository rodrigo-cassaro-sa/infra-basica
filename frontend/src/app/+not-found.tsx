import { Link, Stack } from "expo-router";
import { StyleSheet, Text, View } from "react-native";

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: "Página não encontrada" }} />
      <View style={styles.page}>
        <Text accessibilityRole="header" style={styles.title}>
          Página não encontrada
        </Text>
        <Link href="/" style={styles.link}>
          Voltar para o início
        </Link>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    backgroundColor: "#111827",
    alignItems: "center",
    justifyContent: "center",
    gap: 16,
    padding: 24,
  },
  title: {
    color: "#f9fafb",
    fontSize: 22,
    fontWeight: "700",
  },
  link: {
    color: "#93c5fd",
    fontSize: 16,
    minHeight: 48,
    textAlignVertical: "center",
  },
});
