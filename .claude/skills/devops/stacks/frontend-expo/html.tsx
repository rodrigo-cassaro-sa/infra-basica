// app/+html.tsx — só existe no web com output "static" (Expo Router).
// Carrega /config.js ANTES do bundle, para window.__APP_CONFIG__ existir quando o app iniciar.
import { ScrollViewStyleReset } from "expo-router/html";
import type { PropsWithChildren } from "react";

export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="pt-BR">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        {/* síncrono de propósito: precisa rodar antes do app */}
        <script src="/config.js" />
        <ScrollViewStyleReset />
      </head>
      <body>{children}</body>
    </html>
  );
}
