import React from "react";
import ReactDOM from "react-dom/client";
import InboxCounter from "./InboxCounter";
import EmailTriage from "./EmailTriage";
import EmailDeepDive from "./EmailDeepDive";
import BoardZoomOut from "./BoardZoomOut";
import StatsReveal from "./StatsReveal";
import CTACard from "./CTACard";

const params = new URLSearchParams(window.location.search);
const page = params.get("page");

let Component: React.FC;
switch (page) {
  case "inbox":
    Component = InboxCounter;
    break;
  case "triage":
    Component = EmailTriage;
    break;
  case "deepdive":
    Component = EmailDeepDive;
    break;
  case "zoomout":
    Component = BoardZoomOut;
    break;
  case "stats":
    Component = StatsReveal;
    break;
  case "cta":
    Component = CTACard;
    break;
  default:
    Component = EmailDeepDive;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Component />
  </React.StrictMode>
);
