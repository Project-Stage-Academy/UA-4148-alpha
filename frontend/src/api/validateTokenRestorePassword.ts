import axios from "./index";

export interface RestoreTokenData {
  token: string;
}

export interface RestoreTokenResponse {
  valid: boolean;
}

export async function validateTokenRestorePassword(
  data: RestoreTokenData
): Promise<RestoreTokenResponse> {
  const response = await axios.post<RestoreTokenResponse>(
    "/users/password-restore/",
    data
  );
  return response.data;
}
