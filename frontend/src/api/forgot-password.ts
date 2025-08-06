import axios from "./index";

export interface ResetPasswordData {
  email: string;
}

export interface ResetPasswordResponse {
  message: string;
}

export async function forgotPassword(data: ResetPasswordData): Promise<ResetPasswordResponse> {
  const response = await axios.post<ResetPasswordResponse>("/users/password-reset/", data);
  return response.data;
}
