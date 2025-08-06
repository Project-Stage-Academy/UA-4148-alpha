import { Link } from "react-router-dom";
import { Button } from "../ui/button";
import { useAuthContext } from "@/hooks/useAuthContext";

export function AuthButtons() {
  const auth = useAuthContext();
  return (
    <div className="flex items-center gap-6">
      {auth.user ? (
        <Button variant="tertiary" asChild>
          <Link to="/signin">Мій профіль</Link>
        </Button>
      ) : (
        <>
          <Button variant="tertiary" asChild>
            <Link to="/signin">Увійти</Link>
          </Button>
          <Button>Зареєструватися</Button>
        </>
      )}
    </div>
  );
}
