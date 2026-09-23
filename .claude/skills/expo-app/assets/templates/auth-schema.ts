// DESTINO: src/features/auth/schemas/auth-schema.ts
// Contrato de autenticação — deve bater com docs/contratos-de-api.md (POST /auth/login, /auth/refresh, /auth/logout, GET /auth/me).
import { z } from "zod";

export const sessionUserDtoSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.email(),
  role: z.string(), // ajuste para z.enum([...]) com os papéis do projeto
});

export const loginResponseDtoSchema = z.object({
  accessToken: z.string(),
  refreshToken: z.string().optional(), // na Web o backend usa cookie httpOnly e pode omitir
  user: sessionUserDtoSchema,
});

/** Login só exige "não vazio": regra de força de senha é do CADASTRO, senão quem tem senha antiga não entra. */
export const loginFormSchema = z.object({
  email: z.email("Digite um e-mail válido"),
  password: z.string().min(1, "Digite sua senha"),
});
