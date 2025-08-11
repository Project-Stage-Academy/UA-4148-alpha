import { useSearchParams } from "react-router-dom";

export function EnterprisesAndIndustries() {
  const [searchParams] = useSearchParams();
  return <div>Enterprises and industries {searchParams.get("search")}</div>;
}
