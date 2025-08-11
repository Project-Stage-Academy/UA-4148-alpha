import { Navigation } from "./Navigation";
import { AuthButtons } from "./AuthButtons";
import { Logo } from "./Logo";
import { Search } from "../composed/Search";

export const Header = () => {
  return (
    <header className="bg-main-white border-b border-inactive-60">
      <div className="flex justify-between py-4 px-6 container mx-auto">
        <Logo />
        <div className="flex items-center gap-6">
          <Navigation />
          <Search />
          <AuthButtons />
        </div>
      </div>
    </header>
  );
};
