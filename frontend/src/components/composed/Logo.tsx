import { CraftMergeIcon } from "@/icons/CraftMergeIcon";
import { Link } from "react-router-dom";

export function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <CraftMergeIcon />
      <p className="font-display font-bold uppercase text-2xl text-main-black">
        StartHub
      </p>
    </Link>
  );
}
