import { Outlet } from "react-router-dom";
import { Header } from "./components/composed_ui/Header";

export function Root() {
  return (
    <main className="bg-main-bg h-full">
      <Header />
      <Outlet />
    </main>
  );  
}
