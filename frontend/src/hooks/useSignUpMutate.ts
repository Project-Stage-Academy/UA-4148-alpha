import { signUp, type SignUpData, type SignUpResponse } from "@/api/auth";
import { useMutation } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export function useSignUpMutate() {
  const navigate = useNavigate();
  return useMutation<
    SignUpResponse,
    AxiosError,
    SignUpData
  >({
    mutationFn: signUp,
    onSuccess: () => {
      navigate("/signin");
    },
    onError: (error) => {
      console.log(error);
      if (error.status && error.status >= 500) {
        toast.error("Серверна помилка, спробуйте пізніше");
        return
      }
      if (error.response?.data) {
        throw error.response?.data
      }
      toast.error(
        "Електронна пошта чи пароль вказані некоректно. Спробуйте ще раз."
      );
    },
  });
}
