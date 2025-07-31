import { Outlet } from "react-router-dom";
import { Header } from "./components/composed_ui/Header";

export function Root() {
  return (
    <main>
      <Header />
      <Outlet />
    </main>
  );
}
