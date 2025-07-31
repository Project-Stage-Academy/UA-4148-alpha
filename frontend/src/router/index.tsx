import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Root } from "../Root";

const routes = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [],
  },
]);

export function Router() {
  return <RouterProvider router={routes} />;
}
