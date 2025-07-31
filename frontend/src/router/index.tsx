import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Root } from "../Root";
import { About } from "@/pages/About";
import { EnterprisesAndIndustries } from "@/pages/EnterprisesAndIndustries";

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
    ],
  },
]);

export function Router() {
  return <RouterProvider router={routes} />;
}
