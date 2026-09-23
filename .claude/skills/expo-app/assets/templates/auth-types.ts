// DESTINO: src/features/auth/types/auth-types.ts
import type { z } from "zod";

import type { loginFormSchema, sessionUserDtoSchema } from "../schemas/auth-schema";

export type SessionUser = z.infer<typeof sessionUserDtoSchema>;
export type LoginFormValues = z.infer<typeof loginFormSchema>;
