import { cn } from "@/libs/utils";
import { Link } from "react-router-dom";

export function Navigation({ className }: { className?: string }) {
  return (
    <nav aria-label="Main navigation">
      <ol className={cn("flex gap-6 items-center", className)}>
        <li>
          <Link
            to="/about"
            className="font-display font-medium text-main-gray-100 text-md"
          >
            Про нас
          </Link>
        </li>
        <li>
          <Link
            to="/enterprises-and-industries"
            className="font-display font-medium text-main-gray-100 text-md"
          >
            Підприємства та сектори
          </Link>
        </li>
      </ol>
    </nav>
  );
}
