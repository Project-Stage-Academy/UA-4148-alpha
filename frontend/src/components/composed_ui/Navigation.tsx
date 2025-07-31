import { Link } from "react-router-dom";

export function Navigation() {
  return (
    <nav aria-label="Main navigation">
      <ol className="flex gap-6 items-center">
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
