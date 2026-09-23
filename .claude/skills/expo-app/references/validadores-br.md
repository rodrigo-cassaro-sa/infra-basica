# Validadores e máscaras brasileiros

Copie para `src/utils/validators-br.ts` na primeira vez que o projeto precisar. Sem dependência
externa. Testado: CPF/CNPJ válidos e inválidos, máscaras de celular e fixo.

```ts
// src/utils/validators-br.ts
import { z } from "zod";

export const onlyDigits = (value: string) => value.replace(/\D/g, "");

// ---------- CPF ----------
export function isValidCPF(value: string): boolean {
  const c = onlyDigits(value);
  if (c.length !== 11 || /^(\d)\1{10}$/.test(c)) return false; // rejeita 111.111.111-11
  const digit = (base: string, startWeight: number) => {
    const sum = [...base].reduce((acc, d, i) => acc + Number(d) * (startWeight - i), 0);
    const rest = (sum * 10) % 11;
    return rest === 10 ? 0 : rest;
  };
  return digit(c.slice(0, 9), 10) === Number(c[9]) && digit(c.slice(0, 10), 11) === Number(c[10]);
}

export const maskCPF = (value: string) =>
  onlyDigits(value).slice(0, 11)
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");

export const cpfSchema = z.string().refine(isValidCPF, "Digite um CPF válido (11 números).").transform(onlyDigits);

// ---------- CNPJ (numérico) ----------
export function isValidCNPJ(value: string): boolean {
  const c = onlyDigits(value);
  if (c.length !== 14 || /^(\d)\1{13}$/.test(c)) return false;
  const digit = (base: string) => {
    const weights = base.length === 12 ? [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] : [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const sum = [...base].reduce((acc, d, i) => acc + Number(d) * (weights[i] ?? 0), 0);
    const rest = sum % 11;
    return rest < 2 ? 0 : 11 - rest;
  };
  return digit(c.slice(0, 12)) === Number(c[12]) && digit(c.slice(0, 13)) === Number(c[13]);
}

export const maskCNPJ = (value: string) =>
  onlyDigits(value).slice(0, 14)
    .replace(/(\d{2})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1/$2")
    .replace(/(\d{4})(\d{1,2})$/, "$1-$2");

export const cnpjSchema = z.string().refine(isValidCNPJ, "Digite um CNPJ válido (14 números).").transform(onlyDigits);
// A Receita Federal anunciou CNPJ alfanumérico a partir de jul/2026. Se o projeto precisar
// aceitar o formato novo, confira a regra oficial de cálculo antes de usar este validador.

// ---------- Telefone (celular ou fixo, com DDD) ----------
export function maskPhoneBR(value: string) {
  const d = onlyDigits(value).slice(0, 11);
  if (d.length <= 10) return d.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{4})(\d{1,4})$/, "$1-$2");
  return d.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{5})(\d{1,4})$/, "$1-$2");
}

export const phoneBRSchema = z
  .string()
  .transform(onlyDigits)
  .refine((d) => d.length === 10 || d.length === 11, "Digite o telefone com DDD, como (14) 99999-9999.")
  .refine((d) => d.length === 10 || d[2] === "9", "Celular começa com 9 depois do DDD.");

/** WhatsApp/Evolution API normalmente esperam DDI. */
export const toWhatsAppNumber = (digits: string) => (digits.startsWith("55") ? digits : `55${digits}`);

// ---------- CEP ----------
export const maskCEP = (value: string) => onlyDigits(value).slice(0, 8).replace(/(\d{5})(\d)/, "$1-$2");
export const cepSchema = z.string().transform(onlyDigits).refine((d) => d.length === 8, "Digite um CEP válido (8 números).");

// ---------- Moeda (digitação da direita para a esquerda: "12345" → "123,45") ----------
export function maskMoneyBR(value: string) {
  const d = onlyDigits(value);
  if (!d) return "";
  return (Number(d) / 100).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
export const moneyBRSchema = z
  .string()
  .transform((v) => Number(onlyDigits(v)) / 100)
  .refine((n) => n > 0, "Informe um valor.");
```

CPF, CNPJ, CEP e telefone brasileiros são formato do **dado**, não do idioma: continuam
com máscara brasileira mesmo com o app em outro idioma.

## Endereço por CEP

Ao completar 8 dígitos, o **service** busca o endereço (ViaCEP ou endpoint do seu backend)
e a tela preenche com `form.setValue(campo, valor, { shouldValidate: true })`. A ViaCEP
responde `{ "erro": true }` para CEP inexistente: trate como erro no campo CEP. Deixe os
campos de endereço editáveis mesmo preenchidos — a base não é perfeita.

## Teste

```ts
// src/utils/validators-br.test.ts
import { isValidCPF, maskPhoneBR, phoneBRSchema } from "./validators-br";

it.each(["529.982.247-25", "52998224725"])("aceita CPF %s", (v) => expect(isValidCPF(v)).toBe(true));
it.each(["529.982.247-24", "111.111.111-11", ""])("rejeita CPF %s", (v) => expect(isValidCPF(v)).toBe(false));
it("mascara celular e fixo", () => {
  expect(maskPhoneBR("14999998888")).toBe("(14) 99999-8888");
  expect(maskPhoneBR("1433334444")).toBe("(14) 3333-4444");
});
it("remove máscara na saída", () => expect(phoneBRSchema.parse("(14) 99999-8888")).toBe("14999998888"));
```
