# Formulários

## Sumário
1. Stack e princípio
2. Schema de formulário
3. `FormInput` e props de teclado
4. Tela de formulário completa
5. Erros do servidor (422)
6. Máscaras e dados brasileiros
7. Outros tipos de campo
8. Formulário em etapas
9. Edição (pré-preenchido)
10. Checklist

---

## 1. Stack e princípio

React Hook Form + Zod + `@hookform/resolvers/zod`. Um `useForm` por formulário, nunca
dezenas de `useState`. O envio é uma mutation do TanStack Query (`dados-e-api.md` §5).

Validação no app é UX; o backend revalida sempre com a mesma regra.
Aparência (label, erro, foco, contraste, microcopy): skill `ux-ui` (`componentes.md`,
`conteudo-e-microcopy.md`).

```bash
npx expo install react-hook-form @hookform/resolvers zod
```

## 2. Schema de formulário

Fica em `features/<f>/schemas/<entidade>-schema.ts`, ao lado do DTO schema — são coisas
diferentes: o DTO descreve a API (`snake_case`), o schema de formulário descreve o que o
usuário digita (`camelCase`). O mapper converte (`toUserPayload`).

```ts
// src/features/students/schemas/student-schema.ts
import { z } from "zod";

import { cpfSchema, phoneBRSchema } from "@/utils/validators-br";

export const studentFormSchema = z.object({
  name: z.string().trim().min(3, "Digite o nome completo"),
  phone: phoneBRSchema,
  email: z.email("Digite um e-mail válido, como nome@empresa.com").optional().or(z.literal("")),
  cpf: cpfSchema.optional().or(z.literal("")),
});
```

Mensagens em português, escritas para o usuário final: o que corrigir, não "campo inválido".
Projeto multi-idioma: a mensagem vira chave de tradução (`ux-ui/references/i18n.md` §6).

Schema com `.transform()` (máscara removida) tem tipo de entrada ≠ tipo de saída. Tipe o
form com os dois:

```ts
export type StudentFormInput = z.input<typeof studentFormSchema>;   // o que a tela manipula
export type StudentFormValues = z.output<typeof studentFormSchema>; // o que vai para o mapper

const form = useForm<StudentFormInput, unknown, StudentFormValues>({ resolver: zodResolver(studentFormSchema) });
```

## 3. `FormInput` e props de teclado

`TextInput` não é input do DOM: `register` não funciona no RN. Todo campo usa o
`FormInput` (`src/components/forms/form-input.tsx`, template em `assets/templates/`), que
encapsula `Controller`, label, erro, ajuda, máscara e alvo de toque ≥ 48.

Props obrigatórias em todo campo de texto — cada uma corta atrito real:

| Campo | `keyboardType` | `autoComplete` | `textContentType` (iOS) | Outros |
|---|---|---|---|---|
| Nome | `default` | `name` | `name` | `autoCapitalize="words"` |
| E-mail | `email-address` | `email` | `emailAddress` | `autoCapitalize="none"` |
| Telefone | `phone-pad` | `tel` | `telephoneNumber` | máscara |
| Senha (login) | `default` | `current-password` | `password` | `secureTextEntry` |
| Senha (cadastro) | `default` | `new-password` | `newPassword` | `secureTextEntry` |
| CPF / CEP | `number-pad` | `off` / `postal-code` | — / `postalCode` | máscara |
| Valor em R$ | `decimal-pad` | `off` | — | máscara de moeda |

E ainda: `returnKeyType="next"` + `onSubmitEditing` focando o próximo campo; no último,
`returnKeyType="done"` + `onSubmitEditing={onSubmit}`.

## 4. Tela de formulário completa

```tsx
// src/features/students/screens/student-create-screen.tsx
import { zodResolver } from "@hookform/resolvers/zod";
import { router } from "expo-router";
import { useRef } from "react";
import { useForm } from "react-hook-form";
import { Text, type TextInput } from "react-native";

import { applyFieldErrors, FormInput } from "@/components/forms/form-input";
import { Button, Screen } from "@/components/ui";
import { getUserMessage, ValidationError } from "@/services/api/errors";
import { useTheme } from "@/theme";
import { maskPhoneBR } from "@/utils/validators-br";

import { useCreateStudent } from "../hooks/use-students";
import { studentFormSchema } from "../schemas/student-schema";
import type { StudentFormInput, StudentFormValues } from "../types/student-types";

export function StudentCreateScreen() {
  const { colors, typography } = useTheme();
  const createStudent = useCreateStudent();
  const phoneRef = useRef<TextInput>(null);
  const emailRef = useRef<TextInput>(null);

  const form = useForm<StudentFormInput, unknown, StudentFormValues>({
    resolver: zodResolver(studentFormSchema),
    defaultValues: { name: "", phone: "", email: "", cpf: "" },
    mode: "onTouched", // valida ao sair do campo, não a cada tecla
  });

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      await createStudent.mutateAsync(values);
      router.back();
    } catch (error) {
      if (error instanceof ValidationError && Object.keys(error.fieldErrors).length > 0) {
        applyFieldErrors(form.setError, error.fieldErrors);
      } else {
        form.setError("root.server", { message: getUserMessage(error) });
      }
    }
  });

  return (
    <Screen title="Novo aluno">
      <FormInput
        control={form.control} name="name" label="Nome completo"
        autoCapitalize="words" autoComplete="name" textContentType="name"
        returnKeyType="next" submitBehavior="submit" onSubmitEditing={() => phoneRef.current?.focus()}
      />
      <FormInput
        ref={phoneRef} control={form.control} name="phone" label="WhatsApp"
        keyboardType="phone-pad" autoComplete="tel" textContentType="telephoneNumber"
        mask={maskPhoneBR} returnKeyType="next" onSubmitEditing={() => emailRef.current?.focus()}
      />
      <FormInput
        ref={emailRef} control={form.control} name="email" label="E-mail (opcional)"
        keyboardType="email-address" autoCapitalize="none" autoComplete="email" textContentType="emailAddress"
        returnKeyType="done" onSubmitEditing={onSubmit}
      />

      {form.formState.errors.root?.server ? (
        <Text accessibilityRole="alert" style={[typography.body, { color: colors.danger }]}>
          {form.formState.errors.root.server.message}
        </Text>
      ) : null}

      <Button title="Cadastrar aluno" onPress={onSubmit} loading={createStudent.isPending} />
    </Screen>
  );
}
```

O que não é opcional, e o motivo:
- **Botão com `loading`/desabilitado durante o envio**: toque duplo cria dois registros.
- **`Screen`** (safe area + `KeyboardAvoidingView` + `keyboardShouldPersistTaps="handled"`):
  sem isso o teclado cobre o campo, e o primeiro toque no botão só fecha o teclado.
  Comportamento diferente entre Android e iOS → `react-native-keyboard-controller`
  (`KeyboardAwareScrollView`), que exige development build.
- **`mode: "onTouched"`**: validar a cada tecla mostra "e-mail inválido" antes de a pessoa terminar.
- **Erro nunca apaga o que foi digitado** (regra 8 da `ux-ui`).

## 5. Erros do servidor (422)

Contrato padrão (`docs/contratos-de-api.md`):
`{ "code": "EMAIL_EM_USO", "message": "...", "fieldErrors": { "email": ["Já cadastrado"] } }`.

O `apiClient` converte 400/422 em `ValidationError` com `fieldErrors`. A tela:
1. tem `fieldErrors` → `applyFieldErrors(form.setError, error.fieldErrors)` (foca o primeiro);
2. não tem → `setError("root.server", { message: getUserMessage(error) })` e mostra acima
   do botão. Nunca `error.message` cru.

## 6. Máscaras e dados brasileiros

A máscara é **exibição**: a tela mostra `(14) 99999-9999`, a API recebe `14999999999`.
Aplique com a prop `mask` do `FormInput` e remova no schema com `.transform()`.
Validadores e máscaras prontos (CPF, CNPJ, telefone, CEP, moeda) em `validadores-br.md` →
copie para `src/utils/validators-br.ts` na primeira vez que o projeto precisar.

## 7. Outros tipos de campo

Mesmo padrão (`Controller` + label + erro abaixo), em `src/components/forms/`:

- **Switch / checkbox**: valor booleano, `onValueChange={field.onChange}`,
  `accessibilityRole="switch"`/`"checkbox"` com `accessibilityState={{ checked }}`.
- **Seleção**: até ~5 opções → botões segmentados ou radio; mais que isso → bottom sheet com
  lista e busca (`@expo/ui` tem componentes prontos no SDK 56+). Evite o `Picker` nativo:
  visual diferente por plataforma e ruim na Web.
- **Data/hora**: picker nativo no mobile (via `@expo/ui` ou `@react-native-community/datetimepicker`);
  na Web, campo com máscara `dd/mm/aaaa`. Guarde `Date` no form e envie ISO no mapper.
- **Upload**: backend gera URL pré-assinada; o app envia direto ao storage (`seguranca.md`).

## 8. Formulário em etapas

Um único `useForm` no componente pai; valide só os campos da etapa antes de avançar com
`await form.trigger(["name", "phone"])`. Não crie um `useForm` por etapa. Mostre o progresso
("Etapa 2 de 3") e permita voltar sem perder o que foi digitado.

## 9. Edição (pré-preenchido)

Busque com o hook de query e só renderize o formulário quando o dado chegar, passando como
`defaultValues` (ou `form.reset(dados)` quando chegar). `formState.isDirty` desabilita
"Salvar" enquanto nada mudou e dispara "Descartar alterações?" ao sair
(listener `beforeRemove` da navegação).

## 10. Checklist

```text
[ ] Schema Zod de formulário com mensagens em português; backend valida a mesma regra
[ ] Todos os campos via FormInput (ou irmão em components/forms), nenhum Controller solto na tela
[ ] keyboardType, autoComplete, textContentType e returnKeyType em todo campo de texto
[ ] Teclado não cobre campo nem botão (aparelho pequeno, Android e iOS)
[ ] Botão com loading e bloqueado durante o envio
[ ] 422 aplicado nos campos; demais erros via getUserMessage acima do botão
[ ] Máscara removida no schema quando a API espera só dígitos
[ ] Web conferida (Tab, Enter, foco visível), se o app tem versão web
```
