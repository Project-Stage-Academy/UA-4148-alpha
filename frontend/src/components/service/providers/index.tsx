import type { PropsWithChildren } from "react";
import { queryClient } from "./QueryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./AuthProvider";

export function Providers({ children }: PropsWithChildren) {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </AuthProvider>
  );
}
