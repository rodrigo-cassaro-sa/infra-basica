// DESTINO: src/components/forms/form-input.tsx
// Campo de texto ligado ao React Hook Form: label visível, erro abaixo, alvo de toque ≥ 48, tokens do tema.
// Máscara opcional (exibição); remova a máscara no schema (.transform) antes de enviar.
import type { Ref } from "react";
import { Controller, type Control, type FieldPath, type FieldValues, type UseFormSetError } from "react-hook-form";
import { Text, TextInput, View, type TextInputProps } from "react-native";

import type { FieldErrors } from "@/services/api/errors";
import { MIN_TOUCH_TARGET, useTheme } from "@/theme";

type FormInputProps<T extends FieldValues> = {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  /** Texto de ajuda fixo abaixo do campo (ex.: formato esperado). */
  helper?: string;
  mask?: (value: string) => string;
  /** React 19: ref é prop comum — use para focar o próximo campo (returnKeyType="next"). */
  ref?: Ref<TextInput>;
} & Omit<TextInputProps, "value" | "onChangeText" | "onBlur">;

export function FormInput<T extends FieldValues>({ control, name, label, helper, mask, ref, ...inputProps }: FormInputProps<T>) {
  const { colors, spacing, radius, typography } = useTheme();

  return (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => {
        const error = fieldState.error?.message;
        return (
          <View style={{ gap: spacing.xs, marginBottom: spacing.md }}>
            <Text style={[typography.label, { color: colors.text }]}>{label}</Text>
            <TextInput
              ref={ref}
              accessibilityLabel={label}
              accessibilityHint={error ?? helper}
              value={field.value ?? ""}
              onChangeText={(text) => field.onChange(mask ? mask(text) : text)}
              onBlur={field.onBlur}
              placeholderTextColor={colors.textMuted}
              style={[
                typography.body,
                {
                  color: colors.text,
                  backgroundColor: colors.surface,
                  borderWidth: 1,
                  borderColor: error ? colors.danger : colors.border,
                  borderRadius: radius.md,
                  paddingHorizontal: spacing.md,
                  minHeight: MIN_TOUCH_TARGET,
                },
              ]}
              {...inputProps}
            />
            {error ? (
              <Text accessibilityLiveRegion="polite" style={[typography.caption, { color: colors.danger }]}>
                {error}
              </Text>
            ) : helper ? (
              <Text style={[typography.caption, { color: colors.textMuted }]}>{helper}</Text>
            ) : null}
          </View>
        );
      }}
    />
  );
}

/** Aplica erros de campo vindos do backend (ValidationError / 422) no formulário; foca o primeiro. */
export function applyFieldErrors<T extends FieldValues>(setError: UseFormSetError<T>, fieldErrors: FieldErrors) {
  Object.entries(fieldErrors).forEach(([field, messages], index) => {
    const message = messages[0];
    if (message) setError(field as FieldPath<T>, { type: "server", message }, { shouldFocus: index === 0 });
  });
}
