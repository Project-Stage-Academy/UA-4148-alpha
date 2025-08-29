import { useMutation } from "@tanstack/react-query";
import { signIn, type SignInData, type SignInResponse } from "../api/auth";
import { useAuthContext } from "./useAuthContext";
import type { AxiosError } from "axios";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export function useSignInMutate() {
  const navigate = useNavigate();
  const auth = useAuthContext();
  return useMutation<
    SignInResponse,
    AxiosError<{ detail: string }>,
    SignInData
  >({
    mutationFn: signIn,
    onSuccess: (data) => {
      auth?.login(data);
      navigate("/enterprises-and-industries");
    },
    onError: (error) => {
      console.error(error);
      if (error.status && error.status >= 500) {
        toast.error("Серверна помилка, спробуйте пізніше");
        return;
      }
      if (error.response?.data.detail == "Invalid credentials") {
        toast.error(
          "Електронна пошта чи пароль вказані некоректно. Спробуйте ще раз."
        );
        return;
      }
    },
  });
}
