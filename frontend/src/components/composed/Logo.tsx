import { CraftMergeIcon } from "@/icons/CraftMergeIcon";

export function Logo() {
  return (
    <div className="flex items-center gap-2.5">
      <CraftMergeIcon />
      <p className="font-display font-bold uppercase text-2xl text-main-black">StartHub</p>
    </div>
  );
}
