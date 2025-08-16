import { Navigation } from "./Navigation";
import { AuthButtons } from "./AuthButtons";
import { Logo } from "./Logo";
import { Search } from "../composed/Search";
import { useDesktop } from "@/hooks/useDesktop";
import { MenuIcon } from "@/icons/MenuIcon";
import { cn } from "@/libs/utils";

export const Header = () => {
  const isDesktop = useDesktop();
  return (
    <header className="bg-main-white border-b border-inactive-60">
      <div
        className={cn("flex justify-between max-w-[1304px] py-4 mx-auto", {
          "px-6": isDesktop,
          "px-4": !isDesktop,
        })}
      >
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
