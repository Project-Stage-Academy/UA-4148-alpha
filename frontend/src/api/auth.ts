import axios from "./index";

export interface SignInData {
  email: string;
  password: string;
}

export interface SignInResponse {
  refresh: string;
  access: string;
  user: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    role: null | string;
  };
}

export async function signIn(data: SignInData): Promise<SignInResponse> {
  const response = await axios.post<SignInResponse>("/auth/login/", data);
  return response.data;
}

export interface SignUpData {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  role: "1" | "2";
}

export interface SignUpResponse {
  message: string;
  user_id: string;
  email: string;
}

export async function signUp(data: SignUpData): Promise<SignUpResponse> {
  const response = await axios.post<SignUpResponse>("/users/register/", data);
  return response.data;
}
