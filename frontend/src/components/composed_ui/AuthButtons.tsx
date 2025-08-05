import { Link } from "react-router-dom";
import { Button } from "../ui/button";

export function AuthButtons() {
  return (
    <div className="flex items-center gap-6">
      <Button variant={"tertiary"} asChild>
        <Link to="/signin">Увiйти</Link>
      </Button>
      <Button asChild>
        <Link to="/signup">Зареєструватися</Link>
      </Button>
    </div>
  );
}
