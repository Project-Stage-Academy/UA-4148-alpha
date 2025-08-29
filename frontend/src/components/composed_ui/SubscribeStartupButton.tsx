import { Heart } from "lucide-react";
import { Button } from "../ui/button";
import { useAuthContext } from "@/hooks/useAuthContext";

interface SubscribeStartupButtonProps {
  id: number;
}

const SubscribeStartupButton = ({ id }: SubscribeStartupButtonProps) => {
  const { user } = useAuthContext();
  const handleSubscribe = () => {
    alert("Subscribed to sturtup: " + id);
  };

  if (user?.role != "investor") {
    return;
  }

  // TODO: check if investor subscribed for this startup
  const subscribed = true;
  return (
    <Button variant={"tertiary"} onClick={handleSubscribe}>
      {subscribed ? <Heart className="fill-black" /> : <Heart />}
    </Button>
  );
};

export default SubscribeStartupButton;
