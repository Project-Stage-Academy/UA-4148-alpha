import { Outlet } from "react-router-dom";
import { Header } from "./components/composed/Header";

export function Root() {
  return (
    <main>
      <Header />
      <Outlet />
    </main>
  );
}
