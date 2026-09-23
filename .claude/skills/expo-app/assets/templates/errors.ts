// DESTINO: src/services/api/errors.ts
// Erros tipados da camada HTTP. A UI decide o que fazer pelo tipo, nunca pela mensagem.

export type FieldErrors = Record<string, string[]>;

export class AppError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly code?: string,
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = new.target.name;
  }
}

export class NetworkError extends AppError {}
export class UnauthorizedError extends AppError {}
export class ForbiddenError extends AppError {}
export class NotFoundError extends AppError {}
export class ServerError extends AppError {}
export class ContractError extends AppError {}

export class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly fieldErrors: FieldErrors = {},
    status = 422,
    code?: string,
    requestId?: string,
  ) {
    super(message, status, code, requestId);
  }
}

/** Mensagem segura para mostrar ao usuário. Nunca devolve detalhe técnico. */
export function getUserMessage(error: unknown): string {
  if (error instanceof NetworkError) return "Sem conexão. Verifique sua internet e tente novamente.";
  if (error instanceof UnauthorizedError) return "Sua sessão expirou. Entre novamente.";
  if (error instanceof ForbiddenError) return "Você não tem permissão para fazer isso.";
  if (error instanceof NotFoundError) return "Não encontramos o que você procurou.";
  if (error instanceof ValidationError) return "Confira os campos destacados.";
  return "Algo deu errado. Tente novamente em instantes.";
}
