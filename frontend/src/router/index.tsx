import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Root } from "../Root";
import { About } from "@/pages/About";
import { EnterprisesAndIndustries } from "@/pages/EnterprisesAndIndustries";
import { SignIn } from "@/pages/auth/SignIn";
import { ForgotPassword } from "@/pages/auth/ForgotPassword";

const routes = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        path: "/about",
        element: <About />,
      },
      {
        path: "/enterprises-and-industries",
        element: <EnterprisesAndIndustries />,
      },
      {
        path: "/signin",
        element: <SignIn />,
      },
      {
        path: "/forgot-password",
        element: <ForgotPassword />,
      },
    ],
  },
]);

export function Router() {
  return <RouterProvider router={routes} />;
}
