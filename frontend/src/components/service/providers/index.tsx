import type { PropsWithChildren } from "react";
import { queryClient } from "./QueryClient";
import { QueryClientProvider } from "@tanstack/react-query";

export function Providers({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
