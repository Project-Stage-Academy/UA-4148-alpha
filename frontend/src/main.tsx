import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { Router } from "./router";
import { Providers } from "./components/service/providers";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Providers>
      <Router />
    </Providers>
  </StrictMode>
);
