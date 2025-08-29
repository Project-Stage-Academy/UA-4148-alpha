import { Heart } from "lucide-react";
import { Button } from "../ui/button";

interface SubscribeStartupButtonProps {
  id: number;
}

const SubscribeStartupButton = ({ id }: SubscribeStartupButtonProps) => {
  const handleSubscribe = () => {
    alert("Subscribed to sturtup: " + id);
  };

  const subscribed = true;
  return (
    <Button variant={"tertiary"} onClick={handleSubscribe}>
      {subscribed ? <Heart className="fill-black" /> : <Heart />}
    </Button>
  );
};

export default SubscribeStartupButton;
