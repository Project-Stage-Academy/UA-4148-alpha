import axios from "./index";

export interface RestorePasswordData {
  password: string;
  confirm_password: string;
}

export interface RestorePasswordResponse {
  detail?: string
}

export async function resetPassword(data: RestorePasswordData): Promise<RestorePasswordResponse> {
  const response = await axios.post<RestorePasswordResponse>("/users/password-reset-submission/", data);
  return response.data;
}
