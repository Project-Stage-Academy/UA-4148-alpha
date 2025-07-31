import { Button } from "../ui/button";

export function AuthButtons() {
  return (
    <div className="flex items-center gap-6">
      <Button variant={"tertiary"}>Увiйти</Button>
      <Button>Зареєструватися</Button>
    </div>
  );
}
