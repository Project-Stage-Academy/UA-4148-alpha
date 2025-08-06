import { useMutation } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { useNavigate } from "react-router-dom";
import { forgotPassword, type ResetPasswordData, type ResetPasswordResponse } from "@/api/forgot-password";

export function useForgotPasswordMutate() {
  const navigate = useNavigate();
  return useMutation<
    ResetPasswordResponse,
    AxiosError<{ detail: string }>,
    ResetPasswordData
  >({
    mutationFn: forgotPassword,
    onSuccess: () => {
      navigate("/password-recovery-email-sent");
    },
    onError: () => {
      throw new Error("Зазначена електронна адреса не зареєстрована");
    },
  });
}
