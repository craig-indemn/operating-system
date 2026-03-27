import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import DashboardReveal from "./DashboardReveal";
import CTACard from "./CTACard";

const params = new URLSearchParams(window.location.search);
const page = params.get("page");

let Component: React.FC;
if (page === "dashboard") {
  Component = DashboardReveal;
} else if (page === "cta") {
  Component = CTACard;
} else {
  Component = App;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Component />
  </React.StrictMode>
);
