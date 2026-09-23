// DESTINO: src/services/api/api-client.ts
// Único ponto do app que faz HTTP. Toda resposta é validada pelo schema Zod recebido.
// 401 → tenta refresh UMA vez (single-flight) → repete a request; falhou → limpa sessão.
import { z } from "zod";

import { config } from "@/config/env";
import { tokenStorage } from "@/services/storage/token-storage";
import {
  ContractError,
  ForbiddenError,
  NetworkError,
  NotFoundError,
  ServerError,
  UnauthorizedError,
  ValidationError,
  type FieldErrors,
} from "./errors";

const DEFAULT_TIMEOUT_MS = 15_000;

type RequestOptions = {
  headers?: Record<string, string>;
  signal?: AbortSignal;
  timeoutMs?: number;
  /** false para endpoints públicos (login, cadastro). */
  auth?: boolean;
};

const errorBodySchema = z
  .object({
    code: z.string().optional(),
    message: z.string().optional(),
    fieldErrors: z.record(z.string(), z.array(z.string())).optional(),
  })
  .partial();

/** Chamado quando o refresh falha. Ligue ao logout da sessão no bootstrap do app. */
let onUnauthorized: (() => void) | undefined;
export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

// ---- Refresh de token: um único refresh em andamento; requests com 401 aguardam o mesmo ----
const REFRESH_PATH = "/auth/refresh"; // ajuste ao backend e documente em docs/contratos-de-api.md
const refreshResponseSchema = z.object({ accessToken: z.string(), refreshToken: z.string().optional() });
let refreshing: Promise<boolean> | null = null;

async function refreshTokens(): Promise<boolean> {
  const refreshToken = await tokenStorage.getRefreshToken();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  try {
    const response = await fetch(`${config.apiUrl}${REFRESH_PATH}`, {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      // Mobile manda o refresh token; na Web o backend lê o cookie httpOnly.
      body: JSON.stringify(refreshToken ? { refreshToken } : {}),
      credentials: "include",
      signal: controller.signal,
    });
    if (!response.ok) return false;
    const parsed = refreshResponseSchema.safeParse(await response.json().catch(() => undefined));
    if (!parsed.success) return false;
    await tokenStorage.setTokens(parsed.data);
    return true;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}

async function request<TSchema extends z.ZodType>(
  method: string,
  path: string,
  schema: TSchema,
  body?: unknown,
  options: RequestOptions = {},
  isRetry = false,
): Promise<z.infer<TSchema>> {
  const { auth = true, timeoutMs = DEFAULT_TIMEOUT_MS } = options;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  options.signal?.addEventListener("abort", () => controller.abort());

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
    ...options.headers,
  };

  if (auth) {
    const token = await tokenStorage.getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${config.apiUrl}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
      credentials: "include", // necessário na Web quando a sessão usa cookie httpOnly
    });
  } catch {
    throw new NetworkError("Falha de rede ou timeout");
  } finally {
    clearTimeout(timeout);
  }

  const requestId = response.headers.get("x-request-id") ?? undefined;

  if (response.status === 401 && auth && !isRetry) {
    refreshing ??= refreshTokens().finally(() => {
      refreshing = null;
    });
    if (await refreshing) return request(method, path, schema, body, options, true);
  }

  if (!response.ok) {
    const raw: unknown = await response.json().catch(() => ({}));
    const parsed = errorBodySchema.safeParse(raw);
    const info = parsed.success ? parsed.data : {};
    const message = info.message ?? `HTTP ${response.status}`;
    const fieldErrors: FieldErrors = info.fieldErrors ?? {};

    switch (response.status) {
      case 401:
        if (auth) {
          await tokenStorage.clear();
          onUnauthorized?.();
        }
        throw new UnauthorizedError(message, 401, info.code, requestId);
      case 403:
        throw new ForbiddenError(message, 403, info.code, requestId);
      case 404:
        throw new NotFoundError(message, 404, info.code, requestId);
      case 400:
      case 422:
        throw new ValidationError(message, fieldErrors, response.status, info.code, requestId);
      default:
        throw new ServerError(message, response.status, info.code, requestId);
    }
  }

  const data: unknown = response.status === 204 ? undefined : await response.json().catch(() => undefined);
  const result = schema.safeParse(data);
  if (!result.success) {
    // Backend quebrou o contrato. Loga detalhe técnico, usuário vê mensagem genérica.
    console.warn(`[contract] ${method} ${path}`, z.prettifyError(result.error));
    throw new ContractError(`Resposta fora do contrato em ${method} ${path}`, response.status, undefined, requestId);
  }
  return result.data;
}

export const apiClient = {
  get: <S extends z.ZodType>(path: string, schema: S, options?: RequestOptions) =>
    request("GET", path, schema, undefined, options),
  post: <S extends z.ZodType>(path: string, body: unknown, schema: S, options?: RequestOptions) =>
    request("POST", path, schema, body, options),
  put: <S extends z.ZodType>(path: string, body: unknown, schema: S, options?: RequestOptions) =>
    request("PUT", path, schema, body, options),
  patch: <S extends z.ZodType>(path: string, body: unknown, schema: S, options?: RequestOptions) =>
    request("PATCH", path, schema, body, options),
  delete: <S extends z.ZodType>(path: string, schema: S, options?: RequestOptions) =>
    request("DELETE", path, schema, undefined, options),
};

/** Schema para endpoints sem corpo (204). */
export const noContent = z.undefined();
