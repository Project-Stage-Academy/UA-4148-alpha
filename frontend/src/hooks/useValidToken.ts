import { validateTokenRestorePassword } from "@/api/validateTokenRestorePassword";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

export function useValidToken() {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: validateTokenRestorePassword,
    onSuccess: (data) => {
      if (!data.valid) {
        navigate("/signin");
        return;
      }
    },
    onError: (error) => {
      console.error("Error validating restore token:", error);
    },
  });
}
