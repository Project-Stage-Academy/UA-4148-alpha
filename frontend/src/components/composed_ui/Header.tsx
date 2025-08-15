import { Navigation } from "./Navigation";
import { AuthButtons } from "./AuthButtons";
import { Logo } from "./Logo";
import { Search } from "../composed/Search";
import { useDesktop } from "@/hooks/useDesktop";
import { MenuIcon } from "@/icons/MenuIcon";

export const Header = () => {
  const isDesktop = useDesktop();
  return (
    <header className="bg-main-white border-b border-inactive-60">
      <div className="flex justify-between py-4 px-6 mx-auto">
        <Logo />
        <div className="flex items-center gap-6">
          {isDesktop && (
            <>
              <Navigation />
              <Search />
            </>
          )}
          <div className="flex items-center gap-6">
            <AuthButtons />
            {!isDesktop && <MenuIcon />}
          </div>
        </div>
      </div>
    </header>
  );
};
